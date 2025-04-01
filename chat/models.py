from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    nickname = models.CharField('昵称', max_length=50, blank=True, default='匿名用户')
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.nickname if self.nickname else self.username
    
class ChatMessage(models.Model):
    content = models.TextField('消息内容')
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='发送者'
    )
    room = models.CharField('聊天室', max_length=100)
    timestamp = models.DateTimeField('发送时间', auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['room', '-timestamp']),
        ]

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.sender.id),
            'nickname': self.sender.nickname or self.sender.username,
            'message': self.content,  # 确保字段名统一
            'timestamp': self.timestamp.isoformat()
        }