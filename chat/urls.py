# chat/urls.py
from django.urls import path
from . import views  # 从当前应用导入 views

app_name = 'chat'  # 命名空间

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('room/<str:room_name>/', views.room, name='room'),
]
