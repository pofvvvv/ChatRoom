from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm  # 替换原有的 UserCreationForm


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
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat:room', room_name='lobby')
    else:
        form = CustomUserCreationForm()
    return render(request, 'chat/register.html', {'form': form})

# 用户登录
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('chat:room', room_name='lobby')
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