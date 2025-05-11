# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from .models import Message
# from asgiref.sync import sync_to_async
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = f'chat_{self.room_name}'

#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data['message']
        
#         # Get the authenticated user from the scope
#         user = self.scope["user"]

#         if not user.is_authenticated:
#             await self.send(text_data=json.dumps({
#                 'error': 'User not authenticated'
#             }))
#             return

#         # Save message in the database (ORM in async-safe way)
#         await sync_to_async(Message.objects.create)(
#             room_name=self.room_name,
#             user=user,
#             content=message
#         )

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'user': user.username  # Send username as string
#             }
#         )

#     async def chat_message(self, event):
#         message = event['message']
#         user = event['user']

#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message,
#             'user': user
#         }))
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        # Save message to database
        await self.save_message(username, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'timestamp': timezone.now().isoformat(),
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'timestamp': timestamp,
        }))

    @database_sync_to_async
    def save_message(self, username, message):
        room = Room.objects.get(name=self.room_name)
        Message.objects.create(room=room, user=username, content=message)
