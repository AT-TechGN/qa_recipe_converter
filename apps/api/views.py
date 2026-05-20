import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils import timezone

from apps.core.models import ConversionJob, ExtractedUseCase
from apps.parser.docx_parser import DocxParser
from apps.parser.excel_generator import ExcelGenerator
from apps.parser.file_searcher import search_files
from .serializers import (
    ConversionJobSerializer,
    ConversionJobListSerializer,
    ExtractedUseCaseSerializer,
)

logger = logging.getLogger(__name__)


class UploadAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        word_file = request.FILES.get('word_file')
        if not word_file:
            return Response(
                {'error': 'Le fichier Word est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        excel_template = request.FILES.get('excel_template')

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
                return Response(
                    {'error': job.error_message, 'job_id': str(job.id)},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )

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

            serializer = ConversionJobSerializer(job)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception("API upload error")
            job.status = ConversionJob.Status.ERROR
            job.error_message = str(e)
            job.save()
            return Response(
                {'error': str(e), 'job_id': str(job.id)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class JobDetailAPIView(APIView):
    def get(self, request, job_id):
        job = get_object_or_404(ConversionJob, id=job_id)
        serializer = ConversionJobSerializer(job)
        return Response(serializer.data)


class JobListAPIView(APIView):
    def get(self, request):
        jobs = ConversionJob.objects.all()[:20]
        serializer = ConversionJobListSerializer(jobs, many=True)
        return Response(serializer.data)


class UseCaseUpdateAPIView(APIView):
    def patch(self, request, job_id, uc_id):
        uc = get_object_or_404(ExtractedUseCase, id=uc_id, job_id=job_id)
        serializer = ExtractedUseCaseSerializer(uc, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerateExcelAPIView(APIView):
    def get(self, request, job_id):
        job = get_object_or_404(ConversionJob, id=job_id, status=ConversionJob.Status.DONE)
        use_cases = job.use_cases.all()

        generator = ExcelGenerator(use_cases, job.source_filename)
        excel_buffer = generator.generate()

        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        name = job.source_filename.replace('.docx', '').replace('.doc', '')
        filename = f"recette_{name}_{timestamp}.xlsx"

        response = HttpResponse(
            excel_buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class FileSearchAPIView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        ext_filter = request.query_params.getlist('ext')

        if not query or len(query) < 2:
            return Response({'results': [], 'error': 'Requête trop courte (min 2 caractères)'})

        extensions = ext_filter if ext_filter else None

        try:
            results = search_files(query=query, extensions=extensions, max_results=15)
            return Response({'results': results, 'count': len(results)})
        except Exception as e:
            logger.exception("File search error")
            return Response({'error': str(e), 'results': []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
