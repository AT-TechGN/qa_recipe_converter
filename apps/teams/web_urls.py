"""
Template-based (non-API) URLs for Teams & Projects pages.
"""
from django.urls import path
from . import web_views

urlpatterns = [
    path('',                              web_views.TeamsHomeView.as_view(),    name='teams-home'),
    path('login/',                        web_views.WebLoginView.as_view(),     name='web-login'),
    path('register/',                     web_views.WebRegisterView.as_view(),  name='web-register'),
    path('logout/',                       web_views.WebLogoutView.as_view(),    name='web-logout'),
    path('<slug:slug>/',                  web_views.TeamDashboardPageView.as_view(), name='team-page'),
    path('<slug:slug>/projects/new/',     web_views.CreateProjectPageView.as_view(), name='project-new'),
    path('<slug:slug>/<slug:project_slug>/', web_views.ProjectPageView.as_view(), name='project-page'),
]
