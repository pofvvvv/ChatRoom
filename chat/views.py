from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm  # 替换原有的 UserCreationForm
from rest_framework import viewsets
from chat.serializer import CustomUserSerializer  # 替换原有的 UserSerializer
from .models import CustomUser, ChatMessage  # 添加 ChatMessage 导入
from .serializer import CustomUserSerializer, ChatMessageSerializer  # 添加序列化器导入
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError  # 添加导入


@login_required
def change_nickname(request):
    if request.method == 'POST':
        form = NicknameChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('chat:profile')
    else:
        form = NicknameChangeForm(instance=request.user)
    return render(request, 'chat/change_nickname.html', {'form': form})

# 用户注册
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.data)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return Response({'message': '注册成功'}, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        form = CustomUserCreationForm()
    return render(request, 'chat/register.html', {'form': form})

# 用户登录
@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.data)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return Response({
                    'message': '登录成功',
                    'nickname': getattr(user, "nickname", user.username)
                }, status=status.HTTP_200_OK)
        return Response({'error': '用户名或密码错误'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        form = AuthenticationForm()
    return render(request, 'chat/login.html', {'form': form})

# 用户注销
def user_logout(request):
    logout(request)
    return redirect('chat:login')

@login_required  # 确保用户已登录
def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'username': request.user.username  # 传递当前用户名到模板
    })

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer  # 添加序列化器

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

    def perform_create(self, serializer):
        sender_id = self.request.data.get('sender_id')
        print(f"接收到的请求数据: {self.request.data}")  # 打印整个请求数据
        print(f"接收到的 sender_id: {sender_id}")  # 添加调试信息
        if not sender_id:
            raise ValidationError("sender_id 不能为空")
        serializer.save(sender_id=sender_id)