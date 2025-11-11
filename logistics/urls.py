from rest_framework.routers import DefaultRouter
from .views import AlertViewSet, RecommendationViewSet, InventoryMovementViewSet

router = DefaultRouter()
router.register(r'alerts', AlertViewSet)
router.register(r'recommendations', RecommendationViewSet)
router.register(r'inventory', InventoryMovementViewSet, basename='inventory')
urlpatterns = router.urls
