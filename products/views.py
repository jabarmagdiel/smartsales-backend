from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.db.models import Q
from .models import Category, Product, Price, InventoryMovement, Review
from .serializers import (CategorySerializer, ProductSerializer,ProductDetailSerializer,
                         PriceSerializer, InventoryMovementSerializer, ReviewSerializer)
from users.permissions import IsAdminUser, IsOperator
from logs.models import LogEntry

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]  # Permitir a todos los usuarios autenticados ver categorías
    
    def get_permissions(self):
        """
        Permitir a TODOS ver categorías (GET) sin autenticación,
        pero solo admins pueden crear/modificar/eliminar
        """
        if self.action in ['list', 'retrieve']:
            # CUALQUIERA puede ver categorías (sin autenticación)
            permission_classes = [AllowAny]
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
        Permitir a TODOS ver productos (GET) sin autenticación,
        pero solo admins/operadores pueden crear/modificar/eliminar
        """
        if self.action in ['list', 'retrieve']:
            # CUALQUIERA puede ver productos (sin autenticación)
            permission_classes = [AllowAny]
        else:
            # Solo admins pueden crear/modificar/eliminar productos
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    
    def get_queryset(self):
        queryset = Product.objects.prefetch_related('atributos', 'reviews')
        
        # Filtro de búsqueda
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(sku__icontains=search)
            )
        
        # Filtro por categoría
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filtro por rango de precio
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filtro por disponibilidad
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(stock__gt=0)
        
        # Ordenamiento
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            # Soportar: price, -price, name, -name, created_at, -created_at
            queryset = queryset.order_by(ordering)
        
        return queryset
    
    def get_serializer_class(self):
        """Usar ProductDetailSerializer para retrieve con reseñas"""
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer

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

class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar reseñas de productos
    - list: Ver todas las reseñas (opcionalmente filtradas por producto)
    - create: Crear una nueva reseña (requiere autenticación)
    - retrieve: Ver una reseña específica
    - update/partial_update: Actualizar propia reseña
    - destroy: Eliminar propia reseña
    """
    queryset = Review.objects.all().select_related('product', 'user')
    serializer_class = ReviewSerializer
    
    def get_permissions(self):
        """
        Todos pueden ver reseñas (GET), 
        solo usuarios autenticados pueden crear/modificar/eliminar
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filtrar reseñas por producto si se especifica"""
        queryset = Review.objects.all().select_related('product', 'user')
        
        # Filtrar por producto
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filtrar por rating
        rating = self.request.query_params.get('rating', None)
        if rating:
            queryset = queryset.filter(rating=rating)
        
        # Ordenar por más recientes por defecto
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Guardar reseña con el usuario actual"""
        review = serializer.save(user=self.request.user)
        try:
            LogEntry.objects.create(
                ip_address=self._get_ip(self.request) or 'IP_UNKNOWN',
                user=self.request.user,
                action=f"Reseña creada product_id={review.product.id} rating={review.rating} user={self.request.user.username}"
            )
        except Exception:
            pass
    
    def perform_update(self, serializer):
        """Solo permitir actualizar propias reseñas"""
        if serializer.instance.user != self.request.user and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Solo puedes editar tus propias reseñas")
        
        review = serializer.save()
        try:
            LogEntry.objects.create(
                ip_address=self._get_ip(self.request) or 'IP_UNKNOWN',
                user=self.request.user,
                action=f"Reseña actualizada id={review.id} product_id={review.product.id}"
            )
        except Exception:
            pass
    
    def perform_destroy(self, instance):
        """Solo permitir eliminar propias reseñas"""
        if instance.user != self.request.user and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Solo puedes eliminar tus propias reseñas")
        
        review_id = instance.id
        product_id = instance.product.id
        instance.delete()
        
        try:
            LogEntry.objects.create(
                ip_address=self._get_ip(self.request) or 'IP_UNKNOWN',
                user=self.request.user,
                action=f"Reseña eliminada id={review_id} product_id={product_id}"
            )
        except Exception:
            pass
    
    def _get_ip(self, request):
        """Helper para obtener IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

