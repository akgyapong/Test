from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
import re
import phonenumbers
from phonenumbers import carrier, geocoder

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

@api_view(['POST'])
def user_register(request):
    """User registration endpoint"""
   
    #Get data from User request
    full_name = request.data.get('full_name')
    phone_number= request.data.get('phone_number')
    password = request.data.get('password')

    # Validate required fields
    if not full_name or not phone_number or not password:
        return Response({
            'error': 'Full name, phone number and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    
    # validate phone number format
    is_valid_phone, phone_error = validate_phone_number(phone_number)
    if not is_valid_phone:
        return Response({
            'error': phone_error
        }, status=status.HTTP_400_BAD_REQUEST)

    
    
    # Validate Password Strength
    is_valid_pass, password_error = validate_password(password)
    if not is_valid_pass:
        return Response({
            'error': password_error
        }, status=status.HTTP_400_BAD_REQUEST)
    

    # Checking if phone number already exist
    if User.objects.filter(username=phone_number).exists():
        return Response({
            'error': 'Phone number already exists. Please try a different number'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # split full name into first and last name
    name_parts = full_name.strip().split(' ', 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    # Create new user
    try:
        user=User.objects.create(
            username=phone_number,
            first_name=first_name,
            last_name=last_name,
            password=make_password(password)
        )

        return Response({
            'message': 'User registered successfully',
            'user_id': user.id,
            'full_name': f"{user.first_name} {user.last_name}".strip(),
            'phone_number': user.username
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': 'Failed to create user'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def validate_password(password):
    """Validate password strength"""

    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one Uppercase"
    
    if password.lower() in ['password', '123456','qwerty', 'abc123']:
        return False, "Password is too common"
    
    return True, "Password is valid"

def validate_phone_number(phone_number):
    try:
        #Parse with Ghana context
        parsed = phonenumbers.parse(phone_number, "GH")

        if not phonenumbers.is_valid_number(parsed):
            return False, "Invalid phone number"
        
        #Ensure it's a Ghana mobile number

        if phonenumbers.number_type(parsed) not in [
            phonenumbers.PhoneNumberType.MOBILE,
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE
        ]:
            return False, "Must be a mobile number"
        
        return True, "Phone number is valid"
    
    except phonenumbers.NumberParseException:
        return False, "Invalid Phone number format"


    
@api_view(['POST'])
def user_login(request):
    """User login endpoint"""

    #Get data from request
    phone_number = request.data.get('phone_number')
    password = request.data.get('password')

    #Validate required field
    if not phone_number or not password:
        return Response({
            'error': 'Phone number and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    #Authenticate user (phone_number is stored as username)
    user = authenticate(username=phone_number, password=password)

    if user is not None:
        #User authenticated successful
        return Response({
            'message': 'Login successful',
            'user_id': user.id,
            'full_name': f"{user.first_name} {user.last_name}".strip(),
            'phone_number': user.username
        }, status=status.HTTP_200_OK)
    else:
        #Authentication failed
        return Response({
            'error': 'Invalid phone number or password'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
   

