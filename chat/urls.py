# chat/urls.py
from django.urls import path
from . import views  # 从当前应用导入 views
from rest_framework.routers import DefaultRouter

app_name = 'chat'  # 命名空间

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('room/<str:room_name>/', views.room,name='room'),
]

# 在文件末尾添加DRF路由
router = DefaultRouter()
router.register(r'chatmessages', views.ChatMessageViewSet)
router.register(r'customuser', views.CustomUserViewSet)
urlpatterns += router.urls
