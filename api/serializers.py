from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import re

class UserRegistrationSerializer(serializers.ModelSerializer):
    # Define fields with validation
    phone_number = serializers.CharField(max_length=15, write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(max_length=100, write_only=True)

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'confirm_password', 'full_name']

    def validate_phone_number(self, value):
        """
        Validate phone number format
        """
        original = value.strip()
        
        # Handle international format (+233XXXXXXXXX)
        if original.startswith('+233'):
            after_code = original[4:]
            digits_part = after_code.replace(' ', '').replace('-', '')
            
            if not digits_part.isdigit() or len(digits_part) != 9:
                raise serializers.ValidationError(
                    "International format must be +233 followed by exactly 9 digits"
                )
            return value
        
        # Handle local format (0XXXXXXXXX)
        cleaned = original.replace(' ', '').replace('-', '')
        
        if len(cleaned) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits")
        
        if not cleaned.isdigit():
            invalid_chars = [char for char in cleaned if not char.isdigit()]
            raise serializers.ValidationError(
                f"Invalid characters: {', '.join(set(invalid_chars))}"
            )
        
        if not cleaned.startswith('0'):
            raise serializers.ValidationError("Phone number must start with 0")
        
        return value

    def validate_password(self, value):
        """
        Validate password strength
        """
        # Check minimum length
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        
        # Check for at least one digit
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number")
        
        return value

    def validate(self, data):
        """
        Cross-field validation
        """
        # Check password confirmation
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': "Passwords don't match"
            })
        
        # Normalize phone number for duplicate check
        normalized_phone = self.normalize_phone_number(data['phone_number'])
        
        # Check if phone number already exists
        if User.objects.filter(username=normalized_phone).exists():
            raise serializers.ValidationError({
                'phone_number': 'Phone number already exists. Please try a different number'
            })
        
        return data

    def normalize_phone_number(self, phone_number):
        """
        Normalize phone number to consistent format
        """
        original = phone_number.strip()
        
        # International format (+233XXXXXXXXX) → 233XXXXXXXXX
        if original.startswith('+233'):
            after_code = original[4:]
            digits_part = after_code.replace(' ', '').replace('-', '')
            return '233' + digits_part
        
        # Local format (0XXXXXXXXX) → 233XXXXXXXXX
        cleaned = original.replace(' ', '').replace('-', '')
        if cleaned.startswith('0'):
            return '233' + cleaned[1:]
        
        return cleaned

    def create(self, validated_data):
        """
        Create new user with normalized phone number
        """
        # Remove confirm_password from data
        validated_data.pop('confirm_password')
        
        # Extract and normalize phone number
        phone_number = validated_data.pop('phone_number')
        normalized_phone = self.normalize_phone_number(phone_number)
        
        # Extract full name and split it
        full_name = validated_data.pop('full_name')
        name_parts = full_name.strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Create user
        user = User.objects.create(
            username=normalized_phone,
            first_name=first_name,
            last_name=last_name,
            password=make_password(validated_data['password'])
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_phone_number(self, value):
        """
        Basic phone number validation for login
        """
        if not value.strip():
            raise serializers.ValidationError("Phone number is required")
        return value.strip()

    def validate_password(self, value):
        """
        Basic password validation for login
        """
        if not value:
            raise serializers.ValidationError("Password is required")
        return value

    def normalize_phone_number(self, phone_number):
        """
        Normalize phone number for login lookup
        """
        original = phone_number.strip()
        
        # International format (+233XXXXXXXXX) → 233XXXXXXXXX
        if original.startswith('+233'):
            after_code = original[4:]
            digits_part = after_code.replace(' ', '').replace('-', '')
            return '233' + digits_part
        
        # Local format (0XXXXXXXXX) → 233XXXXXXXXX
        cleaned = original.replace(' ', '').replace('-', '')
        if cleaned.startswith('0'):
            return '233' + cleaned[1:]
        
        return cleaned
