from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Room
from django.contrib.auth.models import User
from django.db.models import Q

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_or_create_room(request):
    user1 = request.user
    user2_username = request.data.get("username")

    if not user2_username:
        return Response({"error": "username required"}, status=400)

    try:
        user2 = User.objects.get(username=user2_username)
    except User.DoesNotExist:
        return Response({"error": "user not found"}, status=404)

    room = Room.objects.filter(
        Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)
    ).first()

    if not room:
        room = Room.objects.create(user1=user1, user2=user2)

    return Response({"room_id": room.id})
