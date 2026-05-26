"""
Django template views for Teams pages (non-API, session auth).
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import Team, TeamMember, Project
from .permissions import can_view_project, can_manage_project


class WebLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('teams-home')
        return render(request, 'teams/login.html')

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if '@' in username:
            from django.contrib.auth.models import User
            try:
                username = User.objects.get(email=username).username
            except User.DoesNotExist:
                pass
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'teams-home'))
        messages.error(request, 'Identifiants invalides.')
        return render(request, 'teams/login.html')


class WebRegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('teams-home')
        return render(request, 'teams/register.html')

    def post(self, request):
        from django.contrib.auth.models import User
        from .serializers import RegisterSerializer
        s = RegisterSerializer(data=request.POST)
        if s.is_valid():
            user = s.save()
            login(request, user)
            messages.success(request, f'Bienvenue, {user.username} !')
            return redirect('teams-home')
        return render(request, 'teams/register.html', {'errors': s.errors})


class WebLogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('web-login')


class TeamsHomeView(LoginRequiredMixin, View):
    login_url = '/teams/login/'

    def get(self, request):
        memberships = TeamMember.objects.filter(
            user=request.user
        ).select_related('team__owner').order_by('-joined_at')
        teams = [m.team for m in memberships]
        return render(request, 'teams/home.html', {'teams': teams})

    def post(self, request):
        """Quick-create a team from the home page form."""
        name = request.POST.get('name', '').strip()
        desc = request.POST.get('description', '').strip()
        if not name:
            messages.error(request, 'Le nom de l\'équipe est requis.')
            return redirect('teams-home')
        team = Team.objects.create(owner=request.user, name=name, description=desc)
        TeamMember.objects.create(team=team, user=request.user, role=TeamMember.Role.OWNER)
        messages.success(request, f'Équipe "{team.name}" créée !')
        return redirect('team-page', slug=team.slug)


class TeamDashboardPageView(LoginRequiredMixin, View):
    login_url = '/teams/login/'

    def get(self, request, slug):
        team = get_object_or_404(Team, slug=slug)
        if not team.is_member(request.user):
            messages.error(request, 'Vous n\'êtes pas membre de cette équipe.')
            return redirect('teams-home')

        projects = [
            p for p in Project.objects.filter(team=team).select_related('created_by')
            if can_view_project(request.user, p)
        ]
        members = team.members.select_related('user').all()
        my_role = team.get_member(request.user)

        from apps.core.models import ConversionJob, ExtractedUseCase
        job_ids = ConversionJob.objects.filter(
            project__in=projects
        ).values_list('id', flat=True)
        ucs = ExtractedUseCase.objects.filter(job_id__in=job_ids)
        uc_total  = ucs.count()
        uc_passed = ucs.filter(status='Passé').count()
        success_rate = round(uc_passed / uc_total * 100, 1) if uc_total > 0 else 0

        recent_jobs = ConversionJob.objects.filter(
            project__in=projects
        ).select_related('project').order_by('-created_at')[:8]

        context = {
            'team': team,
            'projects': projects,
            'members': members,
            'my_role': my_role,
            'can_manage': team.is_admin(request.user),
            'stats': {
                'projects_total':     len(projects),
                'projects_active':    sum(1 for p in projects if p.status == 'active'),
                'projects_archived':  sum(1 for p in projects if p.status == 'archived'),
                'projects_completed': sum(1 for p in projects if p.status == 'completed'),
                'uc_total':   uc_total,
                'uc_passed':  uc_passed,
                'success_rate': success_rate,
                'members_count': members.count(),
            },
            'recent_jobs': recent_jobs,
        }
        return render(request, 'teams/dashboard.html', context)


class CreateProjectPageView(LoginRequiredMixin, View):
    login_url = '/teams/login/'

    def get(self, request, slug):
        team = get_object_or_404(Team, slug=slug)
        if not team.is_admin(request.user):
            messages.error(request, 'Seuls owner/admin peuvent créer un projet.')
            return redirect('team-page', slug=slug)
        return render(request, 'teams/project_form.html', {'team': team})

    def post(self, request, slug):
        team = get_object_or_404(Team, slug=slug)
        if not team.is_admin(request.user):
            messages.error(request, 'Non autorisé.')
            return redirect('team-page', slug=slug)

        name        = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        visibility  = request.POST.get('visibility', 'team')
        icon        = request.POST.get('icon', '').strip()
        color       = request.POST.get('color', '#3B82F6').strip()
        avatar      = request.FILES.get('avatar')

        if not name:
            messages.error(request, 'Le nom du projet est requis.')
            return render(request, 'teams/project_form.html', {'team': team})

        project = Project.objects.create(
            team=team, created_by=request.user,
            name=name, description=description,
            visibility=visibility, icon=icon, color=color,
            avatar=avatar,
        )
        from .models import ProjectMember
        ProjectMember.objects.create(project=project, user=request.user,
                                     role=ProjectMember.Role.LEAD)
        messages.success(request, f'Projet "{project.name}" créé !')
        return redirect('project-page', slug=slug, project_slug=project.slug)


class ProjectPageView(LoginRequiredMixin, View):
    login_url = '/teams/login/'

    def get(self, request, slug, project_slug):
        team    = get_object_or_404(Team, slug=slug)
        project = get_object_or_404(Project, team=team, slug=project_slug)
        if not can_view_project(request.user, project):
            messages.error(request, 'Accès refusé à ce projet.')
            return redirect('team-page', slug=slug)

        from apps.core.models import ConversionJob
        jobs = ConversionJob.objects.filter(project=project).order_by('-created_at')[:20]

        context = {
            'team': team,
            'project': project,
            'can_write': can_view_project(request.user, project),
            'can_manage': can_manage_project(request.user, project),
            'members': project.members.select_related('user').all(),
            'stats': project.stats,
            'recent_jobs': jobs,
        }
        return render(request, 'teams/project_detail.html', context)
