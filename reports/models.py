from django.db import models
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class ReportTemplate(models.Model):
    """Plantillas de reportes predefinidos"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=[
        ('SALES', 'Ventas'),
        ('INVENTORY', 'Inventario'),
        ('CUSTOMERS', 'Clientes'),
        ('FINANCIAL', 'Financiero'),
    ])
    query_template = models.TextField()  # SQL template o configuración
    parameters = models.JSONField(default=dict)  # Parámetros configurables
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class GeneratedReport(models.Model):
    """Reportes generados por usuarios"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    query_text = models.TextField()  # Consulta original del usuario
    query_sql = models.TextField()   # SQL generado
    parameters = models.JSONField(default=dict)
    data = models.JSONField(default=dict)  # Datos del reporte
    format = models.CharField(max_length=20, choices=[
        ('JSON', 'JSON'),
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
        ('CSV', 'CSV'),
    ], default='JSON')
    file_path = models.CharField(max_length=500, blank=True)  # Ruta del archivo generado
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pendiente'),
        ('PROCESSING', 'Procesando'),
        ('COMPLETED', 'Completado'),
        ('ERROR', 'Error'),
    ], default='PENDING')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class VoiceQuery(models.Model):
    """Consultas de voz para reportes"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='voice_queries/', null=True, blank=True)
    transcribed_text = models.TextField()
    interpreted_query = models.TextField()  # Consulta interpretada por IA
    confidence_score = models.FloatField(default=0.0)
    generated_report = models.ForeignKey(GeneratedReport, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Voice Query - {self.user.username} - {self.created_at}"
