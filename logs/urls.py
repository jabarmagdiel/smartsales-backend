from rest_framework.routers import DefaultRouter
from .views import LogEntryViewSet

router = DefaultRouter()
router.register(r'admin/logs', LogEntryViewSet)

urlpatterns = router.urls
