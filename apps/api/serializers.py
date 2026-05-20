from rest_framework import serializers
from apps.core.models import ConversionJob, ExtractedUseCase


class ExtractedUseCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedUseCase
        fields = [
            'id', 'order', 'use_case_id', 'description', 'preconditions',
            'steps', 'expected_results', 'observed_results', 'is_automated', 'status'
        ]


class ConversionJobSerializer(serializers.ModelSerializer):
    use_cases = ExtractedUseCaseSerializer(many=True, read_only=True)

    class Meta:
        model = ConversionJob
        fields = [
            'id', 'created_at', 'status', 'source_filename',
            'use_cases_count', 'error_message', 'use_cases'
        ]


class ConversionJobListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversionJob
        fields = ['id', 'created_at', 'status', 'source_filename', 'use_cases_count']


class UploadSerializer(serializers.Serializer):
    word_file = serializers.FileField()
    excel_template = serializers.FileField(required=False)
