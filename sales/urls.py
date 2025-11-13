from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, CheckoutView, PaymentView, OrderViewSet, OrderManagementViewSet, PaymentManagementView, ReturnViewSet

router = DefaultRouter()
router.register(r'carrito', CartViewSet, basename='cart')
# Alias en inglés para cumplir CU5 (/api/v1/cart/)
router.register(r'cart', CartViewSet, basename='cart-en')
router.register(r'pedidos', OrderViewSet, basename='order')
# Alias para CU7 ventas (/api/v1/ventas/)
router.register(r'ventas', OrderViewSet, basename='ventas')
# Gestión de órdenes para operadores/administradores (CU11)
router.register(r'ordenes', OrderManagementViewSet, basename='order-management')
# Alias para la nueva página de gestión de pedidos
router.register(r'gestion-ordenes', OrderManagementViewSet, basename='order-management-alt')
# Gestión de devoluciones
router.register(r'devoluciones', ReturnViewSet, basename='returns')

urlpatterns = [
    path('checkout/', CheckoutView.as_view({'post': 'checkout'}), name='checkout'),
    path('pago/', PaymentView.as_view({'post': 'process_payment'}), name='process_payment'),
    # Alias plural para CU9 (/api/v1/pagos/)
    path('pagos/', PaymentView.as_view({'post': 'process_payment'}), name='process_payment_plural'),
    # Gestión de pagos para operadores/administradores
    path('gestion-pagos/', PaymentManagementView.as_view(), name='payment_management'),
] + router.urls
