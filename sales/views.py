from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db import transaction
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from django.http import HttpResponse
from io import BytesIO
# Importaciones condicionales para channels
try:
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    HAS_CHANNELS = True
except ImportError:
    HAS_CHANNELS = False
    get_channel_layer = None
    async_to_sync = None
from .models import Cart, CartItem, Order, OrderItem, Payment, Return
from django.core.exceptions import MultipleObjectsReturned
from products.models import Product
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, CheckoutSerializer, PaymentSerializer, ReturnSerializer, ReturnCreateSerializer
from permissions import IsClient
from users.permissions import IsAdminUser, IsOperator
from logs.models import LogEntry

class CartViewSet(viewsets.GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        try:
            cart, _ = Cart.objects.get_or_create(user=self.request.user)
            return cart
        except MultipleObjectsReturned:
            return Cart.objects.filter(user=self.request.user).order_by('id').first()

    def list(self, request):
        try:
            try:
                cart, _ = Cart.objects.get_or_create(user=request.user)
            except MultipleObjectsReturned:
                cart = Cart.objects.filter(user=request.user).order_by('id').first()
            serializer = self.serializer_class(cart)
            return Response(serializer.data)
        except Exception as exc:
            return Response({'detail': 'No se pudo obtener el carrito.', 'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        return self.list(request)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product')
        # Coerce and validate product_id
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            return Response({'detail': 'ID de producto inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            quantity = int(request.data.get('quantity', 1))
        except (TypeError, ValueError):
            quantity = 1
        if quantity < 1:
            quantity = 1

        # Validar existencia del producto
        try:
            Product.objects.only('id').get(id=product_id)
        except (Product.DoesNotExist, ValueError, TypeError):
            return Response({'detail': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            item, created = CartItem.objects.get_or_create(
                cart=cart,
                product_id=product_id,
                defaults={'quantity': quantity}
            )
            if not created:
                item.quantity += quantity
                item.save()
        except Exception as exc:
            return Response({'detail': 'No se pudo agregar al carrito.', 'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        # Refrescar carrito para evitar relaciones en caché
        cart.refresh_from_db()
        serializer = CartSerializer(cart)
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=request.user,
                action=f"Carrito: agregado product_id={product_id} qty={quantity}"
            )
        except Exception:
            pass
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        cart = self.get_object()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        product_id = request.data.get('product')
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            return Response({'detail': 'ID de producto inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()

        # Refrescar carrito para que items reflejen la eliminación
        cart.refresh_from_db()
        serializer = CartSerializer(cart)
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=request.user,
                action=f"Carrito: removido product_id={product_id}"
            )
        except Exception:
            pass
        return Response(serializer.data)

class CheckoutView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        serializer = CheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                total=cart.total,
                shipping_cost=10.00,  # Fixed shipping cost, can be calculated based on method
                address=serializer.validated_data['shipping_address']
            )

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            cart.items.all().delete()  # Clear cart
            
            # Crear garantías automáticas de 1 año para todos los productos
            order.create_warranties()

        # Send WebSocket signal for new order (if channels available)
        if HAS_CHANNELS and get_channel_layer:
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "orders",
                    {
                        "type": "order_created",
                        "message": f"New order #{order.id} created by {request.user.username}",
                        "order_id": order.id
                    }
                )
            except Exception as e:
                # Log error but don't fail the order creation
                print(f"WebSocket notification failed: {e}")
        else:
            print("WebSocket notifications disabled (channels not available)")

        order_serializer = OrderSerializer(order)
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=request.user,
                action=f"Checkout creado order_id={order.id} total={order.total}"
            )
        except Exception:
            pass
        return Response(order_serializer.data)

class PaymentView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def process_payment(self, request):
        order_id = request.data.get('order_id')
        method = request.data.get('method', 'PAYPAL')  # Default to PayPal if not specified
        
        # Debug logging
        print(f"DEBUG: Processing payment - order_id: {order_id}, method: {method}")
        print(f"DEBUG: Request data: {request.data}")
        
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            print(f"DEBUG: Order found - current status: {order.status}")
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        # Validate payment method
        if method not in ['PAYPAL', 'STRIPE', 'CASH']:
            return Response({'error': 'Invalid payment method'}, status=status.HTTP_400_BAD_REQUEST)

        # Handle different payment methods
        if method == 'CASH':
            # Para efectivo: se confirma la orden y se programa pago contra entrega
            payment_status = 'PENDING'
            order.status = 'CONFIRMED'  # Orden confirmada, se enviará y se pagará al entregar
            order.payment_method = 'CASH'
            transaction_id = f"cash_{order.id}_{order.created_at.strftime('%Y%m%d%H%M%S')}"
        else:
            # For online payments (PayPal/Stripe), simulate processing
            payment_status = 'APPROVED' if request.data.get('simulate_success', True) else 'REJECTED'
            transaction_id = f"txn_{order.id}_{method.lower()}"
            order.payment_method = method
            
            if payment_status == 'APPROVED':
                order.status = 'PAID'

        order.save()
        print(f"DEBUG: Order status updated to: {order.status}")

        payment = Payment.objects.create(
            order=order,
            amount=order.total + order.shipping_cost,
            method=method,
            status=payment_status,
            transaction_id=transaction_id
        )
        print(f"DEBUG: Payment created - status: {payment_status}, method: {method}")

        # Simulate FCM notification
        if method == 'CASH':
            print(f"FCM Notification: Order confirmed for cash payment #{order.id}")
            print(f"Message: 'Orden confirmada! Pagarás ${payment.amount} en efectivo al momento de la entrega.'")
        elif payment_status == 'APPROVED':
            print(f"FCM Notification: Payment approved for order #{order.id}")
            print(f"Message: 'Pago de ${payment.amount} procesado exitosamente. Tu orden será enviada pronto.'")

        serializer = PaymentSerializer(payment)
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=request.user,
                action=f"Pago procesado order_id={order.id} metodo={method} status={payment_status} monto={payment.amount}"
            )
        except Exception:
            pass
        return Response({'status': payment_status, 'payment': serializer.data})

class PaymentManagementView(APIView):
    """
    Vista para que operadores/administradores procesen pagos de cualquier orden
    """
    permission_classes = [IsAuthenticated, IsAdminUser | IsOperator]

    def post(self, request):
        order_id = request.data.get('order_id')
        payment_method = request.data.get('payment_method', 'PAYPAL')
        amount = request.data.get('amount')
        
        if not order_id:
            return Response({'error': 'order_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Los operadores/admins pueden procesar pagos de cualquier orden
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Orden no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        # Validar método de pago
        if payment_method not in ['PAYPAL', 'STRIPE', 'CASH']:
            return Response({'error': 'Método de pago inválido'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si ya existe un pago para esta orden
        existing_payment = Payment.objects.filter(order=order).first()
        if existing_payment and existing_payment.status == 'APPROVED':
            return Response({'error': 'Esta orden ya tiene un pago aprobado'}, status=status.HTTP_400_BAD_REQUEST)

        # Simular procesamiento de pago (en producción sería integración real)
        payment_status = 'APPROVED'  # Por defecto aprobado para gestión administrativa
        
        # Crear o actualizar el pago
        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                'amount': amount or (order.total + order.shipping_cost),
                'method': payment_method,
                'status': payment_status,
                'transaction_id': f"admin_txn_{order.id}_{payment_method.lower()}"
            }
        )
        
        if not created:
            # Actualizar pago existente
            payment.method = payment_method
            payment.status = payment_status
            payment.transaction_id = f"admin_txn_{order.id}_{payment_method.lower()}"
            payment.save()

        if payment_status == 'APPROVED':
            # No cambiar a PAID, sino a PROCESSING para seguir el flujo normal
            order.status = 'PROCESSING'
            order.save()
            
            # Crear garantías si no existen
            order.create_warranties()

        serializer = PaymentSerializer(payment)
        
        # Log de la acción
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=request.user,
                action=f"Pago procesado por admin/operador order_id={order.id} metodo={payment_method} status={payment_status} monto={payment.amount}"
            )
        except Exception:
            pass
            
        return Response({
            'status': payment_status, 
            'payment': serializer.data,
            'message': f'Pago procesado exitosamente para la orden #{order.id}'
        })

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def comprobante(self, request, pk=None):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from django.http import HttpResponse
        from io import BytesIO

        order = self.get_object()

        # Create a file-like buffer to receive PDF data
        buffer = BytesIO()

        # Create the PDF object, using the buffer as its "file"
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title = Paragraph("Nota de Venta", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Order details
        order_info = [
            ['Número de Orden:', str(order.id)],
            ['Fecha:', order.created_at.strftime('%Y-%m-%d %H:%M:%S')],
            ['Cliente:', order.user.username],
            ['Dirección de Envío:', order.address],
            ['Estado:', order.status],
            ['Total:', f"${order.total}"],
            ['Costo de Envío:', f"${order.shipping_cost}"],
            ['Total con Envío:', f"${order.total + order.shipping_cost}"],
        ]

        order_table = Table(order_info, colWidths=[150, 300])
        order_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(order_table)
        elements.append(Spacer(1, 12))

        # Items header
        items_title = Paragraph("Productos", styles['Heading2'])
        elements.append(items_title)
        elements.append(Spacer(1, 12))

        # Items table
        data = [['Producto', 'Cantidad', 'Precio Unitario', 'Subtotal']]
        for item in order.items.all():
            data.append([
                item.product.name,
                str(item.quantity),
                f"${item.price}",
                f"${item.subtotal}"
            ])

        items_table = Table(data, colWidths=[200, 80, 100, 100])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(items_table)

        # Build PDF
        doc.build(elements)

        # Get the value of the BytesIO buffer and write it to the response
        pdf = buffer.getvalue()
        buffer.close()

        # Create HTTP response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="nota_venta_{order.id}.pdf"'
        response.write(pdf)

        # Log PDF download
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=request.user,
                action=f"Comprobante descargado order_id={order.id}"
            )
        except Exception:
            pass
        return response

    @action(detail=True, methods=['get'])
    def estado(self, request, pk=None):
        order = self.get_object()
        data = {
            'status': order.status,
            'tracking_url': f'https://tracking.example.com/{order.id}' if order.status == 'SHIPPED' else None
        }
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=request.user,
                action=f"Consulta estado order_id={order.id} status={order.status}"
            )
        except Exception:
            pass
        return Response(data)

    @action(detail=False, methods=['get'])
    def historial(self, request):
        """
        Devuelve el historial de ventas del usuario autenticado (CU7).
        """
        orders = self.get_queryset().order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=request.user,
                action=f"Consulta historial_ordenes count={len(serializer.data)}"
            )
        except Exception:
            pass
        return Response(serializer.data)


class OrderManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que operadores y administradores gestionen todas las órdenes (CU11)
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminUser | IsOperator]
    
    def get_queryset(self):
        # Operadores y administradores pueden ver todas las órdenes
        return Order.objects.all().order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def actualizar_estado(self, request, pk=None):
        """
        Actualizar el estado de una orden
        """
        order = self.get_object()
        new_status = request.data.get('status')
        
        # Validar que el estado sea válido
        valid_statuses = ['PENDING', 'CONFIRMED', 'PAID', 'SHIPPED', 'DELIVERED', 'CANCELLED']
        if new_status not in valid_statuses:
            return Response({'error': 'Estado inválido'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar transiciones de estado lógicas
        current_status = order.status
        
        # Definir transiciones válidas
        valid_transitions = {
            'PENDING': ['CONFIRMED', 'CANCELLED'],
            'CONFIRMED': ['SHIPPED', 'CANCELLED'],  # Para efectivo: CONFIRMED → SHIPPED (se paga al entregar)
            'PAID': ['SHIPPED', 'CANCELLED'],       # Para pagos en línea: PAID → SHIPPED
            'SHIPPED': ['DELIVERED'],
            'DELIVERED': [],  # Estado final
            'CANCELLED': []   # Estado final
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            return Response({
                'error': f'No se puede cambiar de {current_status} a {new_status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Actualizar el estado
        order.status = new_status
        order.save()
        
        # Log de la acción
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=request.user,
                action=f"Estado actualizado order_id={order.id} de {current_status} a {new_status}"
            )
        except Exception:
            pass
        
        serializer = self.get_serializer(order)
        return Response({
            'message': f'Estado actualizado de {current_status} a {new_status}',
            'order': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def confirmar_entrega_y_pago(self, request, pk=None):
        """
        Confirmar entrega y pago para órdenes con pago contra entrega
        """
        order = self.get_object()
        
        if order.status != 'SHIPPED':
            return Response({
                'error': 'Solo se puede confirmar entrega de órdenes enviadas'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Si es pago en efectivo, confirmar el pago también
        if order.payment_method == 'CASH':
            payment = Payment.objects.filter(order=order, method='CASH').first()
            if payment:
                payment.status = 'APPROVED'
                payment.save()
        
        order.status = 'DELIVERED'
        order.save()
        
        # Log de la acción
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=request.user,
                action=f"Entrega confirmada order_id={order.id} pago_efectivo={order.payment_method == 'CASH'}"
            )
        except Exception:
            pass
        
        serializer = self.get_serializer(order)
        return Response({
            'message': 'Entrega confirmada' + (' y pago en efectivo recibido' if order.payment_method == 'CASH' else ''),
            'order': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def comprobante(self, request, pk=None):
        """
        Generar y descargar comprobante PDF de una orden (CU11)
        """
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from django.http import HttpResponse
        from io import BytesIO

        order = self.get_object()

        # Create a file-like buffer to receive PDF data
        buffer = BytesIO()

        # Create the PDF object, using the buffer as its "file"
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title = Paragraph("Nota de Venta", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Order details
        order_info = [
            ['Número de Orden:', str(order.id)],
            ['Fecha:', order.created_at.strftime('%Y-%m-%d %H:%M:%S')],
            ['Cliente:', f"{order.user.first_name} {order.user.last_name} (@{order.user.username})"],
            ['Dirección de Envío:', order.address],
            ['Estado:', order.status],
            ['Total:', f"Bs {order.total}"],
            ['Costo de Envío:', f"Bs {order.shipping_cost}"],
            ['Total con Envío:', f"Bs {float(order.total) + float(order.shipping_cost)}"],
        ]

        order_table = Table(order_info, colWidths=[150, 300])
        order_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(order_table)
        elements.append(Spacer(1, 12))

        # Items header
        items_title = Paragraph("Productos", styles['Heading2'])
        elements.append(items_title)
        elements.append(Spacer(1, 12))

        # Items table
        data = [['Producto', 'Cantidad', 'Precio Unitario', 'Subtotal']]
        for item in order.items.all():
            data.append([
                item.product.name,
                str(item.quantity),
                f"Bs {item.price}",
                f"Bs {item.subtotal}"
            ])

        items_table = Table(data, colWidths=[200, 80, 100, 100])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(items_table)

        # Build PDF
        doc.build(elements)

        # Get the value of the BytesIO buffer and write it to the response
        pdf = buffer.getvalue()
        buffer.close()

        # Create HTTP response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="nota_venta_{order.id}.pdf"'
        response.write(pdf)

        # Log PDF download
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=request.user,
                action=f"Comprobante descargado por operador order_id={order.id}"
            )
        except Exception:
            pass
        return response


class ReturnViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar devoluciones"""
    serializer_class = ReturnSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar devoluciones según el rol del usuario"""
        user = self.request.user
        
        if user.role in ['ADMIN', 'OPERATOR']:
            return Return.objects.all()
        else:
            return Return.objects.filter(user=user)
    
    def get_serializer_class(self):
        """Usar serializer diferente para crear devoluciones"""
        if self.action == 'create':
            return ReturnCreateSerializer
        return ReturnSerializer
    
    def perform_create(self, serializer):
        """Crear devolución y registrar en logs"""
        return_obj = serializer.save()
        
        try:
            ip = self.request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = self.request.META.get('REMOTE_ADDR')
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=self.request.user,
                action=f"Devolución solicitada #{return_obj.id} - Producto: {return_obj.order_item.product.name}"
            )
        except Exception:
            pass
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser | IsOperator])
    def approve(self, request, pk=None):
        """Aprobar una devolución"""
        return_obj = self.get_object()
        
        if return_obj.status != 'REQUESTED':
            return Response(
                {'error': 'Solo se pueden aprobar devoluciones solicitadas'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        refund_amount = request.data.get('refund_amount')
        return_obj.approve(request.user, refund_amount)
        
        serializer = self.get_serializer(return_obj)
        return Response({
            'message': f'Devolución #{return_obj.id} aprobada exitosamente',
            'return': serializer.data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser | IsOperator])
    def reject(self, request, pk=None):
        """Rechazar una devolución"""
        return_obj = self.get_object()
        
        if return_obj.status != 'REQUESTED':
            return Response(
                {'error': 'Solo se pueden rechazar devoluciones solicitadas'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        return_obj.reject(request.user, reason)
        
        serializer = self.get_serializer(return_obj)
        return Response({
            'message': f'Devolución #{return_obj.id} rechazada',
            'return': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def my_orders_for_return(self, request):
        """Obtener órdenes del usuario que pueden ser devueltas"""
        user = request.user
        
        from datetime import timedelta
        from django.utils import timezone
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        orders = Order.objects.filter(
            user=user,
            status__in=['DELIVERED', 'PAID'],
            created_at__gte=thirty_days_ago
        ).prefetch_related('items__product')
        
        orders_data = []
        for order in orders:
            order_data = {
                'id': order.id,
                'created_at': order.created_at,
                'status': order.status,
                'total': order.total,
                'items': []
            }
            
            for item in order.items.all():
                existing_return = Return.objects.filter(
                    order_item=item,
                    status__in=['REQUESTED', 'APPROVED', 'PROCESSING']
                ).first()
                
                item_data = {
                    'id': item.id,
                    'product_id': item.product.id,
                    'product_name': item.product.name,
                    'product_sku': item.product.sku,
                    'quantity': item.quantity,
                    'price': item.price,
                    'subtotal': item.subtotal,
                    'can_return': not existing_return,
                    'existing_return_id': existing_return.id if existing_return else None,
                    'existing_return_status': existing_return.get_status_display() if existing_return else None
                }
                order_data['items'].append(item_data)
            
            orders_data.append(order_data)
        
        return Response(orders_data)
