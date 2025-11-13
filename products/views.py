from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Category, Product, Price, InventoryMovement
from .serializers import CategorySerializer, ProductSerializer, PriceSerializer, InventoryMovementSerializer
from users.permissions import IsAdminUser, IsOperator
from logs.models import LogEntry

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]  # Permitir a todos los usuarios autenticados ver categorías
    
    def get_permissions(self):
        """
        Permitir a todos los usuarios autenticados ver categorías (GET),
        pero solo admins pueden crear/modificar/eliminar
        """
        if self.action in ['list', 'retrieve']:
            # Cualquier usuario autenticado puede ver categorías
            permission_classes = [IsAuthenticated]
        else:
            # Solo admins pueden crear/modificar/eliminar categorías
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  # Permitir a todos los usuarios autenticados ver productos
    
    def get_permissions(self):
        """
        Permitir a todos los usuarios autenticados ver productos (GET),
        pero solo admins/operadores pueden crear/modificar/eliminar
        """
        if self.action in ['list', 'retrieve']:
            # Cualquier usuario autenticado puede ver productos
            permission_classes = [IsAuthenticated]
        else:
            # Solo admins pueden crear/modificar/eliminar productos
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Product.objects.prefetch_related('atributos')

    def _get_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def perform_create(self, serializer):
        product = serializer.save()
        try:
            LogEntry.objects.create(
                ip_address=self._get_ip(self.request) or 'IP_UNKNOWN',
                user=self.request.user,
                action=f"Producto creado id={product.id} name='{getattr(product, 'name', getattr(product, 'nombre', ''))}'"
            )
        except Exception:
            pass

    def perform_update(self, serializer):
        # Capturar estado anterior para diffs
        old = Product.objects.get(pk=serializer.instance.pk)
        product = serializer.save()
        try:
            # Calcular diffs clave
            fields = ['name', 'description', 'category_id', 'sku', 'stock', 'min_stock', 'price']
            changes = []
            for f in fields:
                old_val = getattr(old, f, None)
                new_val = getattr(product, f, None)
                if old_val != new_val:
                    changes.append(f"{f}:{old_val}->{new_val}")
            diff_str = ", ".join(changes) if changes else "sin cambios"
            LogEntry.objects.create(
                ip_address=self._get_ip(self.request) or 'IP_UNKNOWN',
                user=self.request.user,
                action=f"Producto actualizado id={product.id} diffs=[{diff_str}]"
            )
        except Exception:
            pass

    def perform_destroy(self, instance):
        pid = instance.id
        pname = getattr(instance, 'name', getattr(instance, 'nombre', ''))
        instance.delete()
        try:
            LogEntry.objects.create(
                ip_address=self._get_ip(self.request) or 'IP_UNKNOWN',
                user=self.request.user,
                action=f"Producto eliminado id={pid} name='{pname}'"
            )
        except Exception:
            pass

    @action(detail=True, methods=['post'])
    def add_price(self, request, pk=None):
        product = self.get_object()
        serializer = PriceSerializer(data=request.data)
        if serializer.is_valid():
            price = serializer.save(product=product)
            try:
                LogEntry.objects.create(
                    ip_address=self._get_ip(request) or 'IP_UNKNOWN',
                    user=request.user,
                    action=f"Precio agregado producto_id={product.id} price_id={price.id} precio={price.amount if hasattr(price,'amount') else ''}"
                )
            except Exception:
                pass
            return Response(PriceSerializer(price).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put', 'patch'])
    def update_price(self, request, pk=None):
        product = self.get_object()
        price_id = request.data.get('price_id')
        try:
            price = Price.objects.get(id=price_id, product=product)
        except Price.DoesNotExist:
            return Response({'error': 'Price not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PriceSerializer(price, data=request.data, partial=True)
        if serializer.is_valid():
            # Capturar valores anteriores y campos actualizados
            before = {k: getattr(price, k, None) for k in ['amount', 'currency', 'is_active', 'start_date', 'end_date']}
            updated = serializer.save()
            try:
                after = {k: getattr(updated, k, None) for k in before.keys()}
                changes = []
                for k in before.keys():
                    if before[k] != after[k]:
                        changes.append(f"{k}:{before[k]}->{after[k]}")
                diff_str = ", ".join(changes) if changes else "sin cambios"
                LogEntry.objects.create(
                    ip_address=self._get_ip(request) or 'IP_UNKNOWN',
                    user=request.user,
                    action=f"Precio actualizado product_id={product.id} price_id={updated.id} diffs=[{diff_str}]"
                )
            except Exception:
                pass
            return Response(PriceSerializer(updated).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PriceViewSet(viewsets.ModelViewSet):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer
    permission_classes = [IsAdminUser]

class InventoryMovementViewSet(viewsets.ModelViewSet):
    queryset = InventoryMovement.objects.all()
    serializer_class = InventoryMovementSerializer
    permission_classes = [IsOperator]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            movement = serializer.save(user=request.user)
            product = movement.product
            prev_stock = product.stock
            if movement.movement_type == 'IN':
                product.stock += movement.quantity
            elif movement.movement_type == 'OUT':
                if product.stock < movement.quantity:
                    return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
                product.stock -= movement.quantity
            product.save()

        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=request.user,
                action=f"Inventario movimiento={movement.movement_type} product_id={product.id} qty={movement.quantity} stock={prev_stock}->{product.stock}"
            )
        except Exception:
            pass

        serializer = self.get_serializer(movement)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
