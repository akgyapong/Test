from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import re


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
    request=UserRegistrationSerializer,
    responses={
        201: OpenApiResponse(
            description="User registered successfully",
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        'success': True,
                        'message': 'User registered successfully',
                        'data': {
                            'user_id': 1,
                            'username': 'johndoe',
                            'email': 'john@example.com',
                            'full_name': 'John Doe'
                        },
                        'tokens': {
                            'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                            'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
                        }
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description="Registration failed - validation errors",
            examples=[
                OpenApiExample(
                    'Error Response',
                    value={
                        'success': False,
                        'message': 'Registration failed.',
                        'errors': {
                            'email': ['User with this email already exists.']
                        }
                    }
                )
            ]
        )
    },
    summary="Register new user",
    description="Register a new user with email, phone number, password, and optional username. Returns JWT tokens upon successful registration.",
    tags=["Authentication"]
)
@api_view(['POST'])
def user_register(request):
    """User registration endpoint using email, phone, and optional username"""
   
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)

        return Response({
            'success': True,
            'message': 'User registered successfully',
            'data':{
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
            },
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)
# Return validation errors
    return Response({
        'success': False,
        'message': 'Registration failed.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(
    request=UserLoginSerializer,
    responses={
        200: OpenApiResponse(
            description="Login successful",
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        'success': True,
                        'message': 'Login successful',
                        'data': {
                            'user_id': 1,
                            'username': 'johndoe',
                            'email': 'john@example.com',
                            'full_name': 'John Doe'
                        },
                        'tokens': {
                            'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                            'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
                        }
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description="Login failed - invalid credentials",
            examples=[
                OpenApiExample(
                    'Error Response',
                    value={
                        'success': False,
                        'message': 'Login failed.',
                        'errors': {
                            'non_field_errors': ['Invalid credentials.']
                        }
                    }
                )
            ]
        )
    },
    summary="User login",
    description="Login with email or phone number and password. Returns JWT tokens for authentication.",
    tags=["Authentication"]
)
@api_view(['POST'])
def login_user(request):
    """
    User login endpoint - supports email or phone number login
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        # Get the authenticated user from serializer validation
        user = serializer.validated_data['user']

        # Generate JWT tokens
        tokens = get_tokens_for_user(user)

        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
            },
            'tokens': tokens
        }, status=status.HTTP_200_OK)
        
    # Return validation errors
    return Response({
        'success': False,
        'message': 'Login failed.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="Reset code sent successfully",
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            'success': True,
                            'message': 'Reset code sent to your email.',
                            'detail': 'Reset code sent.'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Request failed - validation errors"
            )
        },
        summary="Request password reset",
        description="Request a password reset code. Provide email or phone number.",
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data, context={'ip_address': request.META.get('REMOTE_ADDR')})
        if serializer.is_valid():
            reset_obj = serializer.save()
            # For dev: print code in console. It will be replaced with email/sms in production
            identifier_type = "email" if "@" in reset_obj.phone_number else "phone"
            print(f"Password reset code for {identifier_type} {reset_obj.phone_number}: {reset_obj.reset_code}")
            return Response({
                'success': True,
                'message': f'Reset code sent to your {identifier_type}.',
                'detail': 'Reset code sent.'
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'message': 'Password reset request failed. ',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetConfirmView(APIView):
    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={
            200: OpenApiResponse(
                description="Password reset successful",
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            'success': True,
                            'detail': 'Password reset successful'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Reset failed - invalid code or validation errors"
            )
        },
        summary="Confirm password reset",
        description="Confirm password reset with the code received and set a new password.",
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'detail': 'Password reset successful'
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'message': 'Password reset failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)