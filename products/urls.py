from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, PriceViewSet, InventoryMovementViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'categorias', CategoryViewSet)
router.register(r'productos', ProductViewSet)
router.register(r'precios', PriceViewSet)
router.register(r'movimientos-inventario', InventoryMovementViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = router.urls
