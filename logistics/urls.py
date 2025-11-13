from rest_framework.routers import DefaultRouter
from .views import AlertViewSet, RecommendationViewSet, InventoryMovementViewSet

router = DefaultRouter()
router.register(r'alerts', AlertViewSet)
router.register(r'recommendations', RecommendationViewSet)
router.register(r'inventory', InventoryMovementViewSet, basename='inventory')
# Alias en español para cumplir rutas del examen
router.register(r'alertas', AlertViewSet, basename='alertas')
router.register(r'recomendaciones', RecommendationViewSet, basename='recomendaciones')
urlpatterns = router.urls
