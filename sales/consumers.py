import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

class OrderConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_layer = get_channel_layer()

    async def connect(self):
        await self.channel_layer.group_add(
            "orders",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "orders",
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def order_created(self, event):
        await self.send(text_data=json.dumps({
            'type': 'order_created',
            'message': event['message'],
            'order_id': event['order_id']
        }))

class NotificationConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_layer = get_channel_layer()

    async def connect(self):
        user = self.scope['user']
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            await self.channel_layer.group_add(
                "notificaciones_admin",
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "notificaciones_admin",
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def notification_sent(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message']
        }))
