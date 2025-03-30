from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    nickname = models.CharField('昵称', max_length=50, blank=True, default='匿名用户')
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.nickname if self.nickname else self.username