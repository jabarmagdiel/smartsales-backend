from django.contrib import admin
from .models import ModeloConfiguracion, TrainingSession, HistoricalSale

# Register your models here.
admin.site.register(ModeloConfiguracion)
admin.site.register(TrainingSession)
admin.site.register(HistoricalSale)
