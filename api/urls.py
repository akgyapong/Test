from django.urls import path
from . import views
from .views import PasswordResetConfirmView, PasswordResetRequestView
urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('auth/register/', views.user_register, name='user_register'),
    path('auth/login/', views.login_user, name='login_user'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]