from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('auth/register/', views.user_register, name='user_register')
]
