from rest_framework.routers import DefaultRouter
from .views import AlertViewSet, RecommendationViewSet

router = DefaultRouter()
router.register(r'alerts', AlertViewSet)
router.register(r'recommendations', RecommendationViewSet)

urlpatterns = router.urls
