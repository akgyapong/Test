from django.shortcuts import render
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def auth_info(request):
    """
    API endpoint that provides information about available authentication methods.
    """
    return Response({
        'message': 'Shopwice Authentication API',
        'available_endpoints': {
            'google_login': '/api/v1/auth/google/',
            'facebook_login': '/api/v1/auth/facebook/',
            'description': 'Social authentication endpoints for Shopwice platform'
        },
        'methods': {
            'google': {
                'endpoint': '/api/v1/auth/google/',
                'method': 'POST',
                'required_fields': ['access_token'],
                'description': 'Login with Google OAuth2 access token'
            },
            'facebook': {
                'endpoint': '/api/v1/auth/facebook/',
                'method': 'POST',
                'required_fields':['access_token'],
                'description': 'Login with Facebook OAuth2 access token'
            }
        }
    })

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    
class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    
    