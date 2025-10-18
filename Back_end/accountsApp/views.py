from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .models import Profile

# Create your views here.

@api_view(['POST'])
def register_user(request):
    name = request.data.get("name")
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")

    if not name or not username or not password or not email:
        return Response({"error": "All fields are required."}, status=400)

    if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists():
        return Response({"error": "Email or Username already exists."}, status=400)

    user = User.objects.create_user(first_name=name, username=username, password=password, email=email)
    user.save()
    profile = Profile.objects.create(user=user)
    profile.save()

    return Response({"message": "User registered successfully."})


@api_view(['POST'])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email and password are required."}, status=400)

    user = User.objects.filter(email=email).first()
    if user is None or not user.check_password(password):
        return Response({"error": "Invalid credentials."}, status=400)

    refresh = RefreshToken.for_user(user)
    return Response({
        "message": "Login successful.",
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "username": user.username
    })



@api_view (['GET'])
@permission_classes([IsAuthenticated])
def users_info(request): 

    request_user = request.user
    users = User.objects.exclude(id=request_user.id).order_by('-date_joined')

    data = []
    for user in users:
        data.append({
            "username": user.username,
            "name": user.first_name,
            "email": user.email,
            "avatar": user.profile.avatar.url if user.profile.avatar else None,
            "bio": user.profile.bio if user.profile.bio else None
        })

    return Response(data)


@api_view(['GET'])
def test(request):
    data = {"message": "Test successful.",
            "additional_info": "This is a test endpoint.",
            "status": "OK"
            }
    return Response(data)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response({"error": "Profile not found."}, status=404)

    if request.method == 'GET':
        profile_data = {
            "username": user.username,
            "name": user.first_name,
            "email": user.email,
            "bio": profile.bio,
            "avatar": profile.avatar.url if profile.avatar else None
        }
        return Response(profile_data)

    elif request.method in ['PUT', 'PATCH']:
        bio = request.data.get("bio", profile.bio)
        avatar = request.FILES.get("avatar", None)

        profile.bio = bio
        if avatar:
            profile.avatar = avatar
        profile.save()

        return Response({"message": "Profile updated successfully."})