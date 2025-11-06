from django.db import models

class ReporteDinamico(models.Model):
    prompt_original = models.TextField(help_text="El texto del comando o prompt original enviado por el usuario.")
    consulta_resultante = models.TextField(help_text="La consulta SQL o representación de la consulta ORM resultante.")
    results = models.JSONField(help_text="Los resultados de la consulta en formato JSON.", default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ReporteDinamico - {self.created_at}"
