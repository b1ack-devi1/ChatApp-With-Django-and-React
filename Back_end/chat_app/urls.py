"""
URL configuration for chat_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ChatApp.views import get_or_create_room
from accountsApp.views import profile_view, register_user,users_info,login_user, test
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf.urls.static import static
from chat_app.settings import MEDIA_ROOT, MEDIA_URL
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_user, name='login'),
    path('register/', register_user, name='register'),
    path('users/', users_info, name='users'),
    path("get-room/", get_or_create_room, name="get-room"),
    path("test/", test, name="test"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', profile_view, name='profile'),
    ] + static(MEDIA_URL, document_root=MEDIA_ROOT)
