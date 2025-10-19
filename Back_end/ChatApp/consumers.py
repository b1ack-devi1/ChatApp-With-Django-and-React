import json
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from urllib.parse import parse_qs

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        from django.conf import settings
        from django.contrib.auth.models import User
        # Parse room id from query string
        query_params = parse_qs(self.scope["query_string"].decode())
        self.room_id = query_params.get("room", [None])[0]
        token = query_params.get("token", [None])[0]

        if not self.room_id or not token:
            await self.close()
            return


        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            self.user = await database_sync_to_async(User.objects.get)(id=payload["user_id"])
            
            
        except Exception as e:
            await self.close()
            

            return

        self.room_group_name = f"chat_{self.room_id}"
        

        # Add user to the channel layer group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_status",
                "username": self.user.username,
                "status": "online",
            }
        )

        

        # Load last 50 messages safely
        messages = await self.get_last_messages(self.room_id)
        for msg in messages:
            await self.send(text_data=json.dumps(msg))  # msg is already a dict

    async def disconnect(self, close_code):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_status",
                "username": self.user.username,
                "status": "offline",
            }
        )
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        from django.contrib.auth.models import User
        from django.conf import settings
        
        data = json.loads(text_data)
        message_text = data.get("message")
        query_params = parse_qs(self.scope["query_string"].decode())
        token = query_params.get("token", [None])[0]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = await database_sync_to_async(User.objects.get)(id=payload["user_id"])

        

        if not message_text or not user.is_authenticated:
            
            return

        # Save message safely
        room = await self.get_room(self.room_id)
        message_data = await self.save_message(room, user, message_text)
        

        # Send message to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_data["message"],
                "username": message_data["username"],
                "timestamp": message_data["timestamp"],
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "username": event["username"],
            "timestamp": event["timestamp"],
        }))

    async def user_status(self, event):
        # Send active status update to frontend
        await self.send(text_data=json.dumps({
            "type": "status",
            "username": event["username"],
            "status": event["status"],
        }))


    # -----------------------------
    # Async-safe DB operations
    # -----------------------------
    @database_sync_to_async
    def get_last_messages(self, room_id):
        from .models import Message
        # prefetch sender to avoid lazy DB hits in async loop
        messages = Message.objects.filter(room_id=room_id).select_related("sender").order_by("timestamp")[:50]
        # convert to dicts to send safely
        return [
            {
                "message": msg.content,
                "username": msg.sender.username,
                "timestamp": msg.timestamp.strftime("%H:%M")
            } for msg in messages
        ]

    @database_sync_to_async
    def get_room(self, room_id):
        from .models import Room
        return Room.objects.get(id=room_id)

    @database_sync_to_async
    def save_message(self, room, sender, content):
        from .models import Message
        msg = Message.objects.create(room=room, sender=sender, content=content)
        return {
            "message": msg.content,
            "username": sender.username,
            "timestamp": msg.timestamp.strftime("%H:%M")
        }
