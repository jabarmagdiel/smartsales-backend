from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from django.http import HttpResponse
from io import BytesIO
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Cart, CartItem, Order, OrderItem, Payment
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, CheckoutSerializer, PaymentSerializer
from permissions import IsClient

class CartViewSet(viewsets.GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        return self.get_queryset().first()

    def list(self, request):
        cart = self.get_object()
        if not cart:
            cart = Cart.objects.create(user=request.user)
        serializer = self.serializer_class(cart)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        return self.list(request)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        cart = self.get_object()
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        product_id = request.data.get('product')
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

class CheckoutView(viewsets.ViewSet):
    permission_classes = [IsClient]

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

        # Send WebSocket signal for new order
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "orders",
            {
                "type": "order_created",
                "message": f"New order #{order.id} created by {request.user.username}",
                "order_id": order.id
            }
        )

        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data)

class PaymentView(viewsets.ViewSet):
    permission_classes = [IsClient]

    @action(detail=False, methods=['post'])
    def process_payment(self, request):
        order_id = request.data.get('order_id')
        method = request.data.get('method', 'PAYPAL')  # Default to PayPal if not specified
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        # Validate payment method
        if method not in ['PAYPAL', 'STRIPE']:
            return Response({'error': 'Invalid payment method'}, status=status.HTTP_400_BAD_REQUEST)

        # Simulate payment processing
        payment_status = 'APPROVED' if request.data.get('simulate_success', True) else 'REJECTED'

        payment = Payment.objects.create(
            order=order,
            amount=order.total + order.shipping_cost,
            method=method,
            status=payment_status,
            transaction_id=f"txn_{order.id}_{method.lower()}"
        )

        if payment_status == 'APPROVED':
            order.status = 'PAID'
            order.save()

            # Simulate FCM notification for successful payment
            # In production, this would integrate with Firebase Cloud Messaging
            print(f"FCM Notification: Payment approved for order #{order.id}")
            print(f"Message: 'Your payment of ${payment.amount} has been processed successfully.'")

        serializer = PaymentSerializer(payment)
        return Response({'status': payment_status, 'payment': serializer.data})

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

        return response

    @action(detail=True, methods=['get'])
    def estado(self, request, pk=None):
        order = self.get_object()
        return Response({
            'status': order.status,
            'tracking_url': f'https://tracking.example.com/{order.id}' if order.status == 'SHIPPED' else None
        })
