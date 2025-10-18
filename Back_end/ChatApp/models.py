from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="room_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="room_user2")
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user1.username} & {self.user2.username}"



class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} in {self.room.id}: {self.content[:20]}"
