from rest_framework import serializers
from .models import *
from .models import ChatMessage

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'nickname', 'avatar']  # 确保字段名正确

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'content', 'sender', 'room', 'timestamp']
        depth = 1  # 显示嵌套的 sender 对象信息