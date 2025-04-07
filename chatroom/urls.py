from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('chat/', include('chat.urls')),
    path('', TemplateView.as_view(template_name='index.html')),
]