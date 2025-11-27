from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.hashers import make_password
from .models import PasswordReset
from django.utils import timezone
import re
from .utils import validate_password_strength


class UserRegistrationSerializer(serializers.ModelSerializer):
    # Define fields with custom error messages
    username = serializers.CharField(
        max_length=150, 
        write_only=True, 
        required=False, 
        allow_blank=True,
        error_messages={
            'max_length': 'Username cannot be longer than 150 characters.'
        }
    )
    email = serializers.EmailField(
        write_only=True,
        error_messages={
            'required': 'Email address is required.',
            'blank': 'Email address cannot be blank.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    phone_number = serializers.CharField(
        max_length=15, 
        write_only=True,
        error_messages={
            'required': 'Phone number is required.',
            'blank': 'Phone number cannot be blank.',
            'max_length': 'Phone number cannot be longer than 15 characters.'
        }
    )
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        error_messages={
            'required': 'Password is required.',
            'blank': 'Password cannot be blank.',
            'min_length': 'Password must be at least 8 characters long.'
        }
    )
    confirm_password = serializers.CharField(
        write_only=True,
        error_messages={
            'required': 'Password confirmation is required.',
            'blank': 'Password confirmation cannot be blank.'
        }
    )
    full_name = serializers.CharField(
        max_length=100, 
        write_only=True,
        error_messages={
            'required': 'Full name is required.',
            'blank': 'Full name cannot be blank.',
            'max_length': 'Full name cannot be longer than 100 characters.'
        }
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'confirm_password', 'full_name']

    def validate_phone_number(self, value):
        """
        Validate phone number format (required field)
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Phone number is required.")
            
        original = value.strip()
        
        # Handle international format (+233XXXXXXXXX)
        if original.startswith('+233'):
            after_code = original[4:]
            digits_part = after_code.replace(' ', '').replace('-', '')
            
            if not digits_part.isdigit() or len(digits_part) != 9:
                raise serializers.ValidationError(
                    "Invalid international format. Please use +233 followed by exactly 9 digits (e.g., +233501234567)."
                )
            return value
        
        # Handle local format (0XXXXXXXXX)
        cleaned = original.replace(' ', '').replace('-', '')
        
        if len(cleaned) != 10:
            raise serializers.ValidationError(
                "Phone number must be exactly 10 digits. Please use format like 0501234567."
            )
        
        if not cleaned.isdigit():
            invalid_chars = [char for char in cleaned if not char.isdigit()]
            raise serializers.ValidationError(
                f"Phone number contains invalid characters: {', '.join(set(invalid_chars))}. Only numbers, spaces, and dashes are allowed."
            )
        
        if not cleaned.startswith('0'):
            raise serializers.ValidationError(
                "Local phone number must start with 0. Please use format like 0501234567."
            )
        
        return value

    def validate_username(self, value):
        """
        Validate username uniqueness (optional field)
        """
        # If username is provided, check uniqueness
        if value and value.strip():
            if len(value.strip()) < 3:
                raise serializers.ValidationError("Username must be at least 3 characters long.")
            if User.objects.filter(username=value.strip()).exists():
                raise serializers.ValidationError("This username is already taken. Please choose a different username.")
        return value

    def validate_email(self, value):
        """
        Validate email uniqueness
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Email address is required.")
            
        if User.objects.filter(email=value.lower().strip()).exists():
            raise serializers.ValidationError("An account with this email address already exists. Please use a different email or try logging in.")
        return value.lower().strip()

    def validate_full_name(self, value):
        """
        Validate full name
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Full name is required.")
            
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Full name must be at least 2 characters long.")
            
        return value.strip()

    def validate_password(self, value):
        """
        Validate password strength
        """
        
        return validate_password_strength(value)

    def validate(self, data):
        """
        Cross-field validation with detailed error messages
        """
        errors = {}
        
        # Check password confirmation
        if data.get('password') != data.get('confirm_password'):
            errors['confirm_password'] = "Passwords don't match. Please make sure both password fields are identical."
        
        # Normalize and check phone number uniqueness
        phone_number = data.get('phone_number')
        if phone_number:
            try:
                normalized_phone = self.normalize_phone_number(phone_number)
                
                # Check if phone number already exists in username (old users)
                if User.objects.filter(username=normalized_phone).exists():
                    errors['phone_number'] = "This phone number is already registered. Please use a different number or try logging in."
                
                # Check if phone number already exists in profiles (new users)
                if User.objects.filter(normalized_phone=normalized_phone).exists():
                    errors['phone_number'] = "This phone number is already registered. Please use a different number or try logging in."
                    
            except serializers.ValidationError as e:
                errors['phone_number'] = str(e.detail[0]) if hasattr(e, 'detail') else str(e)
        
        if errors:
            raise serializers.ValidationError(errors)
        
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
        Create new user with email and phone as login identifiers
        """
        # Remove confirm_password from data
        validated_data.pop('confirm_password')
        
        # Extract fields
        username = validated_data.pop('username', '')
        email = validated_data.pop('email')
        phone_number = validated_data.pop('phone_number')
        
        # Normalize phone number to use as primary username
        normalized_phone = self.normalize_phone_number(phone_number)
        
        # Use normalized phone as username if no custom username provided
        final_username = username.strip() if username and username.strip() else normalized_phone
        
        # Extract full name and split it
        full_name = validated_data.pop('full_name')
        name_parts = full_name.strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Create user
        user = User.objects.create(
            username=final_username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=make_password(validated_data['password'])
        )
        
        # Create user profile with phone number
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login with email or phone number
    """
    email = serializers.EmailField(
        required = False,
        allow_blank = True,
        error_messages={
            'invalid': 'Please enter a valid email'
        }
    )
    phone_number = serializers.CharField(
        max_length=15,
        required = False,
        allow_blank = True,
        error_messages={
            'max_length': 'Phone number cannot be longer than 15 characters'
        }
    )
    password = serializers.CharField(
        write_only=True,
        error_messages={
            'required': 'Password is required.',
            'blank': 'Password cannot be blank.'
        }
    )

    def validate_email(self, value):
        """
        Basic validation for email login
        """
        if value and value.strip():
            return value.lower().strip()
        return value
    
    def validate_phone_number(self, value):
        """
        Validation for phone number
        """
        if not value or not value.strip():
            return value
        
        original = value.strip()

        if original.startswith('+233'):
            after_code = original[4:]
            digits_part = after_code.replace(' ', '').replace('-', '')

            if not digits_part.isdigit() or len(digits_part) != 9:
                raise serializers.ValidationError(
                    "Invalid phone number format. (e.g., +223565435654)."

                )
            return value
        
        # Handle local format
        cleaned = original.replace(' ', ''). replace('-', '')

        if len(cleaned) != 10:
            raise serializers.ValidationError(
                "Phone number must be exactly 10 digits."
            )
        if not cleaned.isdigit():
            invalid_chars = [char for char in cleaned if not char.isdigit()]
            raise serializers.ValidationError(
                f"Phone number contains invalid characters: {', '. join(set(invalid_chars))}. Only numbers, spaces and dashes are allowed."

            )
       
        if not cleaned.startswith('0'):
           raise serializers.ValidationError(
            "Phone number must start with 0. Please use the format like 02345465332"
        )
        return value
   
    

    def validate_password(self, value):
        """
        Basic password validation for login with error messages
        """
        if not value:
            raise serializers.ValidationError("Password is required.")
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

    def validate(self, data):
        """
        Validate login credentials
        """
        email = data.get('email', '').strip() if data.get('email') else ''
        phone_number = data.get('phone_number', '').strip() if data.get('phone_number') else ''
        password = data.get('password', '')

        # Ensuring that at least one of phone number or email is used for login
        if not email and not phone_number:
            raise serializers.ValidationError({
                'non_field_errors' : 'Please provide either email or phone number to log in'
            })
        # Ensure only one login method is used
        if email and phone_number:
            raise serializers.ValidationError({
               'non_field_errors': 'Please use either email or phone number, not both.'
            })
        
        if not password:
            raise serializers.ValidationError({
                'password': 'Password is required'
            })
        
        user = None

        if email:
            # Login with email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'email': 'No account found with this email address.'
                })
            
        if phone_number:
                #Login with phone number
             try:
                normalized_phone = self.normalize_phone_number(phone_number)
                try:
                    user = User.objects.get(username=normalized_phone)
                except User.DoesNotExist:
                    # Try profile lookup
                        profile = User.objects.get(normalized_phone=normalized_phone)
             except (Exception, User.DoesNotExist):
                 raise serializers.ValidationError({
                     'phone_number' : 'No account found with this phone number.'
                })

        # Check Password
        if user and not user.check_password(password):
         
            raise serializers.ValidationError({
                    ' Password': 'Incorrect password.'
                    })
        
        if  user and not user.is_active:
            raise serializers.ValidationError({
                'non_field_errors': 'Account is disabled.'
            })
        data['user']= user 
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    reset_identifier = serializers.CharField(max_length=255, help_text="Email or phone number")
    
    def is_email(self, identifier):
        """
        Check if identifier is an email
        """
        return '@' in identifier
    
    def normalize_phone_number(self, phone_number):
        """
        Normalize phone number for lookup
        """
        original = phone_number.strip()
        if original.startswith('+233'):
            after_code = original[4:]
            digits_part = after_code.replace(' ', '').replace('-', '')
            return '233' + digits_part
        cleaned = original.replace(' ', '').replace('-', '')
        if cleaned.startswith('0'):
            return '233' + cleaned[1:]
        return cleaned
    
    def validate(self, value):
        """
        Validate password reset request with detailed error messages
        """
        # value is an OrderedDict, extract the reset_identifier string
        reset_identifier = value.get('reset_identifier', '').strip()
        
        if not reset_identifier:
            raise serializers.ValidationError({
                'reset_identifier': 'Email or phone number is required.'
            })
        
        user = None
        
        if self.is_email(reset_identifier):
            # Reset with email
            try:
                user = User.objects.get(email=reset_identifier.lower())
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'reset_identifier': 'No account found with this email address. Please check your email or register for a new account.'
                })
        else:
            # Reset with phone number - check both username and profile
            try:
                normalized = self.normalize_phone_number(reset_identifier)
            except Exception:
                raise serializers.ValidationError({
                    'reset_identifier': 'Invalid phone number format. Please use format like 0501234567 or +233501234567.'
                })
                
            try:
                # First try to find by username (for backward compatibility)
                user = User.objects.get(username=normalized)
            except User.DoesNotExist:
                try:
                    # Then try to find by profile phone number
                    profile = User.objects.get(normalized_phone=normalized)
                except User.DoesNotExist:
                    raise serializers.ValidationError({
                        'reset_identifier': 'No account found with this phone number. Please check your phone number or register for a new account.'
                    })
        
        # Store for create method
        value['user'] = user
        value['is_email'] = self.is_email(reset_identifier)
        
        return value
    
    def create(self, validated_data):
        user = validated_data['user']
        reset_identifier = validated_data['reset_identifier']
        is_email = validated_data['is_email']
        
        # For phone_number field in model:
        # - If email reset: store email in phone_number field (we'll handle this in confirm)
        # - If phone reset: store normalized phone in phone_number field
        if is_email:
            identifier_for_storage = reset_identifier  # Store email as-is
        else:
            identifier_for_storage = self.normalize_phone_number(reset_identifier)
        
        reset = PasswordReset.objects.create(
            user=user,
            phone_number=identifier_for_storage,  # This field will store either email or phone
            ip_address=self.context.get('ip_address')
        )
        return reset
    


class PasswordResetConfirmSerializer(serializers.Serializer):
    reset_identifier = serializers.CharField(max_length=255, help_text="Email or phone number (same as used in reset request)")
    reset_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def is_email(self, identifier):
        """
        Check if identifier is an email
        """
        return '@' in identifier

    def normalize_phone_number(self, phone_number):
        """
        Normalize phone number for lookup
        """
        original = phone_number.strip()
        if original.startswith('+233'):
            after_code = original[4:]
            digits_part = after_code.replace(' ', '').replace('-', '')
            return '233' + digits_part
        cleaned = original.replace(' ', '').replace('-', '')
        if cleaned.startswith('0'):
            return '233' + cleaned[1:]
        return cleaned

    def validate(self, data):
        """
        Validate password reset confirmation with detailed error messages
        """
        reset_identifier = data.get('reset_identifier', '').strip()
        reset_code = data.get('reset_code', '').strip()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        errors = {}
        
        # Validate required fields
        if not reset_identifier:
            errors['reset_identifier'] = 'Email or phone number is required.'
            
        if not reset_code:
            errors['reset_code'] = 'Reset code is required.'
            
        if not new_password:
            errors['new_password'] = 'New password is required.'
            
        if not confirm_password:
            errors['confirm_password'] = 'Password confirmation is required.'
        
        # Check password match
        if new_password and confirm_password and new_password != confirm_password:
            errors['confirm_password'] = "Passwords don't match. Please make sure both password fields are identical."
        
        # Validate password strength
        if new_password:
            try:
                validate_password_strength(new_password)
            except serializers.ValidationError as e:
                errors['new_password'] = str(e.detail[0]) if hasattr(e, 'detail') else str(e)
        
        if errors:
            raise serializers.ValidationError(errors)
        
        # Determine lookup value based on identifier type
        if self.is_email(reset_identifier):
            # For email reset, look up by email (stored in phone_number field)
            lookup_value = reset_identifier.lower()
        else:
            # For phone reset, look up by normalized phone
            try:
                lookup_value = self.normalize_phone_number(reset_identifier)
            except Exception:
                raise serializers.ValidationError({
                    'reset_identifier': 'Invalid phone number format. Please use format like 0501234567 or +233501234567.'
                })
        
        try:
            reset = PasswordReset.objects.get(
                phone_number=lookup_value,  # This field stores either email or normalized phone
                reset_code=reset_code,
                is_used=False
            )
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError({
                'non_field_errors': 'Invalid or expired reset code. Please request a new password reset.'
            })

        if reset.is_expired():
            raise serializers.ValidationError({
                'non_field_errors': 'This reset code has expired. Please request a new password reset.'
            })

        data['reset_obj'] = reset
        return data

    def save(self):
        """
        Reset the user's password
        """
        reset_obj = self.validated_data['reset_obj']
        new_password = self.validated_data['new_password']
        
        # Update user password
        user = reset_obj.user
        user.set_password(new_password)
        user.save()
        
        # Mark reset as used
        reset_obj.mark_as_used()
        
        return user


# Additional serializers for API documentation

class HealthCheckSerializer(serializers.Serializer):
    """Serializer for health check response"""
    status = serializers.CharField(help_text="API health status")
    message = serializers.CharField(help_text="Health check message")
    timestamp = serializers.DateTimeField(help_text="Server timestamp")
    version = serializers.CharField(help_text="API version")

class UserResponseSerializer(serializers.Serializer):
    """Serializer for user data in API responses"""
    user_id = serializers.IntegerField(help_text="User ID")
    username = serializers.CharField(help_text="Username")
    email = serializers.EmailField(help_text="Email address")
    full_name = serializers.CharField(help_text="User's full name")

class TokenResponseSerializer(serializers.Serializer):
    """Serializer for JWT token response"""
    refresh = serializers.CharField(help_text="JWT refresh token")
    access = serializers.CharField(help_text="JWT access token")

class AuthSuccessResponseSerializer(serializers.Serializer):
    """Serializer for successful authentication response"""
    success = serializers.BooleanField(help_text="Success status")
    message = serializers.CharField(help_text="Response message")
    data = UserResponseSerializer(help_text="User data")
    tokens = TokenResponseSerializer(help_text="JWT tokens")

class AuthErrorResponseSerializer(serializers.Serializer):
    """Serializer for authentication error response"""
    success = serializers.BooleanField(help_text="Success status")
    message = serializers.CharField(help_text="Error message")
    errors = serializers.DictField(help_text="Validation errors")

class PasswordResetSuccessResponseSerializer(serializers.Serializer):
    """Serializer for successful password reset response"""
    success = serializers.BooleanField(help_text="Success status")
    message = serializers.CharField(help_text="Response message")
    detail = serializers.CharField(help_text="Additional details")





