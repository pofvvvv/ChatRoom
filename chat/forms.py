from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    nickname = forms.CharField(label='昵称', max_length=50, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'nickname', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.nickname = self.cleaned_data['nickname']
        if commit:
            user.save()
        return user
    
class NicknameChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['nickname']
        labels = {'nickname': '新昵称'}
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control'})
        }   