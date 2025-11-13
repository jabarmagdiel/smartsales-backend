from rest_framework import serializers
from .models import ReportTemplate, GeneratedReport, VoiceQuery

class ReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = ['id', 'name', 'description', 'category', 'parameters', 'created_at']

class GeneratedReportSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = GeneratedReport
        fields = [
            'id', 'title', 'description', 'template_name', 
            'query_text', 'parameters', 'data', 'format', 
            'status', 'created_at', 'completed_at'
        ]
        read_only_fields = ['user', 'query_sql', 'file_path', 'error_message']

class VoiceQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceQuery
        fields = [
            'id', 'transcribed_text', 'interpreted_query', 
            'confidence_score', 'created_at'
        ]
        read_only_fields = ['user', 'generated_report']
