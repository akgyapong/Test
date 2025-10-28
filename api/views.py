from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
import re
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
# import phonenumbers
# from phonenumbers import carrier, geocoder

def get_tokens_for_user(user):
    """
    Generate JWT tokens for authenticated user
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@extend_schema(
    summary="Health Check",
    description="Check if the API is running and healthy",
    responses={
        200: {
            'description': 'API is healthy and running',
            'examples': {
                'application/json': {
                    'status': 'healthy',
                    'message': 'API is running successfully',
                    'timestamp': '2025-10-21T10:30:00Z',
                    'version': '1.0.0'
                }
            }
        }
    },
    tags=['System']
)
@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint to verify API is working
    """
    data = {
        'status': 'healthy',
        'message': 'API is running successfully',
        'timestamp': timezone.now(),
        'version': '1.0.0'
    }
    return Response(data, status=status.HTTP_200_OK)

@extend_schema(
    summary="User Registration",
    description="Register a new user with phone number, password, and full name",
    request=UserRegistrationSerializer,
    responses={
        201: {
            'description': 'User created successfully',
            'examples': {
                'application/json': {
                    'success': True,
                    'message': 'User registered successfully',
                    'data': {
                        'user_id': 123,
                        'full_name': 'John Doe',
                        'phone_number': '233501234567'
                    },
                    'tokens': {
                        'access': 'eyJ0eXAi...',
                        'refresh': 'eyJ0eXAi...'
                    }
                }
            }
        },
        400: {
            'description': 'Validation error',
            'examples': {
                'application/json': {
                    'success': False,
                    'errors': {
                        'phone_number': ['Phone number already exists']
                    }
                }
            }
        }
    },
    tags=['Authentication']
)
@api_view(['POST'])
def user_register(request):
    """User registration endpoint using serializers"""
   
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)

        return Response({
            'success': True,
            'message': 'User registered successfully',
            'data':{
                'user_id': user.id,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'phone_number': user.username
            },
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)
# Return validation errors
    return Response({
        'success': False,
        'errors': serializer.errors

    }, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(
    summary="User Login",
    description="Authenticate user with phone number and password",
    request=UserLoginSerializer,
    responses={
        200: {
            'description': 'Login successful',
            'examples': {
                'application/json': {
                    'success': True,
                    'message': 'Login successful',
                    'data': {
                        'user_id': 123,
                        'full_name': 'John Doe',
                        'phone_number': '233501234567'
                    },
                    'tokens': {
                        'access': 'eyJ0eXAi...',
                        'refresh': 'eyJ0eXAi...'
                    }
                }
            }
        },
        400: {
            'description': 'Validation error',
            'examples': {
                'application/json': {
                    'success': False,
                    'errors': {
                        'phone_number': ['This field is required'],
                        'password': ['This field is required']
                    }
                }
            }
        },
        401: {
            'description': 'Authentication failed',
            'examples': {
                'application/json': {
                    'success': False,
                    'error': 'Invalid phone number or password'
                }
            }
        }
    },
    tags=['Authentication']
)
@api_view(['POST'])
def login_user(request):
    """
    User login endpoint - completely new implementation
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']

        normalized_phone = serializer.normalize_phone_number(phone_number)
        
        user = authenticate(username=normalized_phone, password=password)

        if user is None:
            user = authenticate(username=phone_number, password=password)

        if user is not None:
            #Generate JWT tokens
            tokens= get_tokens_for_user(user)

            return Response({
                'success': True,
                'message': 'Login successful',
                'data': {
                    'user_id': user.id,
                    'full_name': f"{user.first_name} {user.last_name}".strip(),
                    'phone_number': user.username
                },
                'tokens': tokens
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'Invalid phone number or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
# Return validation errors
    return Response({
    'success': False,
    'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)