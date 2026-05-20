import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.contrib import messages
from django.utils import timezone

from .models import ConversionJob, ExtractedUseCase
from .forms import UploadForm
from apps.parser.docx_parser import DocxParser
from apps.parser.excel_generator import ExcelGenerator

logger = logging.getLogger(__name__)


class IndexView(View):
    template_name = 'core/index.html'

    def get(self, request):
        form = UploadForm()
        recent_jobs = ConversionJob.objects.filter(
            status=ConversionJob.Status.DONE
        )[:5]
        return render(request, self.template_name, {
            'form': form,
            'recent_jobs': recent_jobs,
        })

    def post(self, request):
        form = UploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        word_file = form.cleaned_data['word_file']
        excel_template = form.cleaned_data.get('excel_template')

        job = ConversionJob.objects.create(
            source_filename=word_file.name,
            word_file=word_file,
            excel_template=excel_template,
            status=ConversionJob.Status.PROCESSING,
        )

        try:
            parser = DocxParser(job.word_file.path)
            use_cases = parser.extract_use_cases()

            if not use_cases:
                job.status = ConversionJob.Status.ERROR
                job.error_message = "Aucun tableau de cas de tests détecté dans le document."
                job.save()
                messages.error(request, job.error_message)
                return redirect('core:index')

            for idx, uc_data in enumerate(use_cases):
                ExtractedUseCase.objects.create(
                    job=job,
                    order=idx + 1,
                    use_case_id=uc_data.get('use_case_id', ''),
                    description=uc_data.get('description', ''),
                    preconditions=uc_data.get('preconditions', ''),
                    steps=uc_data.get('steps', ''),
                    expected_results=uc_data.get('expected_results', ''),
                    observed_results=uc_data.get('observed_results', ''),
                )

            job.use_cases_count = len(use_cases)
            job.status = ConversionJob.Status.DONE
            job.save()

            return redirect('core:preview', job_id=job.id)

        except Exception as e:
            logger.exception(f"Erreur lors du traitement du fichier {word_file.name}")
            job.status = ConversionJob.Status.ERROR
            job.error_message = str(e)
            job.save()
            messages.error(request, f"Erreur lors du traitement : {e}")
            return redirect('core:index')


class PreviewView(View):
    template_name = 'core/preview.html'

    def get(self, request, job_id):
        job = get_object_or_404(ConversionJob, id=job_id)
        use_cases = job.use_cases.all()
        return render(request, self.template_name, {
            'job': job,
            'use_cases': use_cases,
            'use_cases_json': json.dumps([{
                'id': str(uc.id),
                'order': uc.order,
                'use_case_id': uc.use_case_id,
                'description': uc.description,
                'preconditions': uc.preconditions,
                'steps': uc.steps,
                'expected_results': uc.expected_results,
                'observed_results': uc.observed_results,
                'is_automated': uc.is_automated,
                'status': uc.status,
            } for uc in use_cases]),
        })

    def post(self, request, job_id):
        """Save manual edits from preview page."""
        job = get_object_or_404(ConversionJob, id=job_id)
        try:
            data = json.loads(request.body)
            for uc_data in data.get('use_cases', []):
                uc = get_object_or_404(ExtractedUseCase, id=uc_data['id'], job=job)
                uc.use_case_id = uc_data.get('use_case_id', uc.use_case_id)
                uc.description = uc_data.get('description', uc.description)
                uc.preconditions = uc_data.get('preconditions', uc.preconditions)
                uc.steps = uc_data.get('steps', uc.steps)
                uc.expected_results = uc_data.get('expected_results', uc.expected_results)
                uc.observed_results = uc_data.get('observed_results', uc.observed_results)
                uc.is_automated = uc_data.get('is_automated', uc.is_automated)
                uc.status = uc_data.get('status', uc.status)
                uc.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class GenerateExcelView(View):
    def get(self, request, job_id):
        job = get_object_or_404(ConversionJob, id=job_id, status=ConversionJob.Status.DONE)
        use_cases = job.use_cases.all()

        generator = ExcelGenerator(use_cases, job.source_filename)
        excel_buffer = generator.generate()

        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"recette_{job.source_filename.replace('.docx', '').replace('.doc', '')}_{timestamp}.xlsx"

        response = HttpResponse(
            excel_buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class ResultView(View):
    template_name = 'core/result.html'

    def get(self, request, job_id):
        job = get_object_or_404(ConversionJob, id=job_id)
        return render(request, self.template_name, {'job': job})
