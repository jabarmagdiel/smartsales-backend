from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderTracking

@receiver(pre_save, sender=Order)
def track_order_status_change(sender, instance, **kwargs):
    """
    Signal para crear un registro de tracking cuando cambia el estado de la orden
    """
    if instance.pk:  # Si la orden ya existe (es una actualización)
        try:
            old_order = Order.objects.get(pk=instance.pk)
            if old_order.status != instance.status:
                # El estado ha cambiado, crear registro de tracking después del guardado
                instance._status_changed = True
                instance._old_status = old_order.status
        except Order.DoesNotExist:
            pass

@receiver(post_save, sender=Order)
def create_tracking_record(sender, instance, created, **kwargs):
    """
    Crear registro de tracking al crear una orden o cuando cambia el estado
    """
    if created:
        # Orden nueva - crear primer registro de tracking
        OrderTracking.objects.create(
            order=instance,
            status=instance.status,
            notes=f"Pedido creado - Método de pago: {instance.get_payment_method_display()}"
        )
        
        # Calcular fecha estimada de entrega (5-7 días hábiles)
        if not instance.estimated_delivery:
            instance.estimated_delivery = timezone.now() + timedelta(days=7)
            instance.save(update_fields=['estimated_delivery'])
    
    elif hasattr(instance, '_status_changed') and instance._status_changed:
        # El estado cambió - crear registro de tracking
        OrderTracking.objects.create(
            order=instance,
            status=instance.status,
            notes=f"Estado actualizado de {instance._old_status} a {instance.status}"
        )
        
        # Limpiar el flag
        delattr(instance, '_status_changed')
        delattr(instance, '_old_status')
