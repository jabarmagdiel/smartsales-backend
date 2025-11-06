from django.urls import path
from .views import QueryReportView, GenerateReportView

app_name = 'reportes'

urlpatterns = [
    path('query/', QueryReportView.as_view(), name='query_report'),
    path('generate/', GenerateReportView.as_view(), name='generate_report'),
]
