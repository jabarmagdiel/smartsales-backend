from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Return, Warranty
from .serializers import ReturnSerializer, WarrantySerializer
from permissions import IsClient
from users.permissions import IsAdminUser, IsOperator
from sales.models import Order, OrderItem
from django.utils import timezone
from datetime import timedelta

class ReturnViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que los clientes gestionen sus devoluciones
    """
    serializer_class = ReturnSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Solo devoluciones del usuario autenticado"""
        return Return.objects.filter(
            order__user=self.request.user
        ).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Crear nueva devolución"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # El serializer ya maneja la validación de order_item
        return_obj = serializer.save()
        
        return Response({
            'id': return_obj.id,
            'message': 'Solicitud de devolución creada exitosamente',
            'status': return_obj.status,
            'product_name': return_obj.product.name
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def available_orders(self, request):
        """
        Obtener órdenes del usuario que pueden ser devueltas
        """
        user = request.user
        
        # Obtener órdenes DELIVERED del usuario
        orders = Order.objects.filter(
            user=user,
            status='DELIVERED'
        ).order_by('-created_at')
        
        result = []
        for order in orders:
            items = []
            order_items = OrderItem.objects.filter(order=order)
            for item in order_items:
                # Verificar si ya hay devolución para este producto
                existing_return = Return.objects.filter(
                    order=order,
                    product=item.product
                ).first()
                
                can_return = not existing_return or existing_return.status == 'REJECTED'
                
                items.append({
                    'id': item.id,
                    'product_id': item.product.id,
                    'product_name': item.product.name,
                    'product_sku': item.product.sku,
                    'quantity': item.quantity,
                    'price': str(item.price),
                    'can_return': can_return,
                    'existing_return_status': existing_return.status if existing_return else None
                })
            
            if items:  # Solo incluir órdenes con items
                result.append({
                    'id': order.id,
                    'order_number': f'ORD-{order.id:06d}',
                    'created_at': order.created_at.isoformat(),
                    'status': order.status,
                    'total': str(order.total),
                    'items': items
                })
        
        return Response(result)

class ReturnManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que administradores gestionen todas las devoluciones
    """
    queryset = Return.objects.all().order_by('-created_at')
    serializer_class = ReturnSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        """Aprobar devolución"""
        return_obj = self.get_object()
        if return_obj.status != 'PENDING':
            return Response(
                {'error': 'Solo se pueden aprobar devoluciones pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return_obj.status = 'APPROVED'
        return_obj.processed_by = request.user
        return_obj.save()
        
        return Response({
            'message': 'Devolución aprobada exitosamente',
            'status': return_obj.status
        })
    
    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        """Rechazar devolución"""
        return_obj = self.get_object()
        if return_obj.status != 'PENDING':
            return Response(
                {'error': 'Solo se pueden rechazar devoluciones pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return_obj.status = 'REJECTED'
        return_obj.processed_by = request.user
        return_obj.save()
        
        return Response({
            'message': 'Devolución rechazada',
            'status': return_obj.status
        })
    
    @action(detail=True, methods=['patch'])
    def process(self, request, pk=None):
        """Procesar devolución aprobada"""
        return_obj = self.get_object()
        if return_obj.status != 'APPROVED':
            return Response(
                {'error': 'Solo se pueden procesar devoluciones aprobadas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Devolver stock
            product = return_obj.product
            product.stock += return_obj.quantity
            product.save()
            
            # Cambiar estado
            return_obj.status = 'PROCESSED'
            return_obj.processed_by = request.user
            return_obj.save()
        
        return Response({
            'message': 'Devolución procesada exitosamente',
            'status': return_obj.status,
            'stock_updated': True
        })


class WarrantyViewSet(viewsets.ModelViewSet):
    queryset = Warranty.objects.all()
    serializer_class = WarrantySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filtrar garantías para que cada cliente solo vea las suyas
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            # Administradores pueden ver todas las garantías
            return Warranty.objects.all().order_by('-start_date')
        else:
            # Clientes solo ven garantías de sus propias órdenes
            return Warranty.objects.filter(
                order__user=user
            ).order_by('-start_date')


class WarrantyManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que administradores gestionen todas las garantías (CU14)
    """
    queryset = Warranty.objects.all().order_by('-start_date')
    serializer_class = WarrantySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @action(detail=True, methods=['patch'])
    def activate(self, request, pk=None):
        """
        Activar una garantía
        """
        warranty = self.get_object()
        warranty.is_active = True
        warranty.save()
        return Response({'status': 'Garantía activada'})
    
    @action(detail=True, methods=['patch'])
    def deactivate(self, request, pk=None):
        """
        Desactivar una garantía
        """
        warranty = self.get_object()
        warranty.is_active = False
        warranty.save()
        return Response({'status': 'Garantía desactivada'})
    
    @action(detail=True, methods=['patch'])
    def resolve(self, request, pk=None):
        """
        Marcar garantía como resuelta
        """
        warranty = self.get_object()
        warranty.resolution_status = 'RESOLVED'
        warranty.save()
        return Response({'status': 'Garantía marcada como resuelta'})
    
    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        """
        Rechazar reclamación de garantía
        """
        warranty = self.get_object()
        warranty.resolution_status = 'REJECTED'
        warranty.save()
        return Response({'status': 'Reclamación de garantía rechazada'})


class ReturnManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que operadores y administradores gestionen devoluciones (CU13)
    """
    queryset = Return.objects.all().order_by('-created_at')
    serializer_class = ReturnSerializer
    permission_classes = [IsAuthenticated, IsAdminUser | IsOperator]
    
    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        """
        Aprobar una devolución
        """
        return_obj = self.get_object()
        if return_obj.status != 'PENDING':
            return Response(
                {'error': 'Solo se pueden aprobar devoluciones pendientes'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return_obj.status = 'APPROVED'
        return_obj.processed_by = request.user
        return_obj.save()
        
        serializer = self.get_serializer(return_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        """
        Rechazar una devolución
        """
        return_obj = self.get_object()
        if return_obj.status != 'PENDING':
            return Response(
                {'error': 'Solo se pueden rechazar devoluciones pendientes'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return_obj.status = 'REJECTED'
        return_obj.processed_by = request.user
        return_obj.save()
        
        serializer = self.get_serializer(return_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def process(self, request, pk=None):
        """
        Procesar una devolución aprobada (devolver stock)
        """
        return_obj = self.get_object()
        if return_obj.status != 'APPROVED':
            return Response(
                {'error': 'Solo se pueden procesar devoluciones aprobadas'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Devolver stock al inventario
            product = return_obj.product
            product.stock += return_obj.quantity
            product.save()
            
            # Marcar como procesado
            return_obj.status = 'PROCESSED'
            return_obj.processed_by = request.user
            return_obj.save()
        
        serializer = self.get_serializer(return_obj)
        return Response(serializer.data)


class WarrantyManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que operadores y administradores gestionen garantías (CU14)
    """
    queryset = Warranty.objects.all().order_by('-start_date')
    serializer_class = WarrantySerializer
    permission_classes = [IsAuthenticated, IsAdminUser | IsOperator]
    
    @action(detail=True, methods=['patch'])
    def activate(self, request, pk=None):
        """
        Activar una garantía
        """
        warranty = self.get_object()
        warranty.is_active = True
        warranty.save()
        
        serializer = self.get_serializer(warranty)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def deactivate(self, request, pk=None):
        """
        Desactivar una garantía
        """
        warranty = self.get_object()
        warranty.is_active = False
        warranty.save()
        
        serializer = self.get_serializer(warranty)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def resolve(self, request, pk=None):
        """
        Marcar garantía como resuelta
        """
        warranty = self.get_object()
        warranty.resolution_status = 'RESOLVED'
        warranty.save()
        
        serializer = self.get_serializer(warranty)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def reject_claim(self, request, pk=None):
        """
        Rechazar reclamación de garantía
        """
        warranty = self.get_object()
        warranty.resolution_status = 'REJECTED'
        warranty.save()
        
        serializer = self.get_serializer(warranty)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Obtener solo garantías activas y vigentes
        """
        from django.utils import timezone
        active_warranties = self.queryset.filter(
            is_active=True,
            end_date__gte=timezone.now()
        )
        serializer = self.get_serializer(active_warranties, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """
        Obtener garantías expiradas
        """
        from django.utils import timezone
        expired_warranties = self.queryset.filter(
            end_date__lt=timezone.now()
        )
        serializer = self.get_serializer(expired_warranties, many=True)
        return Response(serializer.data)
