from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Category, Product, Price, InventoryMovement
from .serializers import CategorySerializer, ProductSerializer, PriceSerializer, InventoryMovementSerializer
from permissions import IsAdmin, IsOperator

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Product.objects.prefetch_related('atributos')

    @action(detail=True, methods=['post'])
    def add_price(self, request, pk=None):
        product = self.get_object()
        serializer = PriceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PriceViewSet(viewsets.ModelViewSet):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer
    permission_classes = [IsAdmin]

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
            if movement.movement_type == 'IN':
                product.stock += movement.quantity
            elif movement.movement_type == 'OUT':
                if product.stock < movement.quantity:
                    return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
                product.stock -= movement.quantity
            product.save()

        serializer = self.get_serializer(movement)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
