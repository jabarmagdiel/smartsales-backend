from rest_framework.routers import DefaultRouter
from .views import ReportTemplateViewSet, ReportsViewSet

router = DefaultRouter()
router.register(r'templates', ReportTemplateViewSet, basename='report-templates')
router.register(r'reports', ReportsViewSet, basename='reports')

urlpatterns = router.urls
