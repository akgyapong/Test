from django.urls import path
from .views import GoogleLogin, FacebookLogin, auth_info

urlpatterns = [
    path('', auth_info, name='auth_info'),
    path('google/', GoogleLogin.as_view(), name='google_login') ,
    path('facebook/', FacebookLogin.as_view(), name='facebook_login')
]