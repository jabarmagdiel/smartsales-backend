from rest_framework.routers import DefaultRouter
from .views import ReturnViewSet, WarrantyViewSet, ReturnManagementViewSet, WarrantyManagementViewSet

router = DefaultRouter()
# Devoluciones para clientes
router.register(r'devoluciones', ReturnViewSet, basename='returns')
# Garantías para clientes
router.register(r'garantias', WarrantyViewSet)
# Gestión de devoluciones para administradores (CU13)
router.register(r'gestion-devoluciones', ReturnManagementViewSet, basename='return-management')
# Gestión de garantías para administradores (CU14)
router.register(r'gestion-garantias', WarrantyManagementViewSet, basename='warranty-management')

urlpatterns = router.urls
