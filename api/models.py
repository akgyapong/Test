from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random, string

class UserProfile(models.Model):
    """
    Extended user profile to store additional user information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    normalized_phone = models.CharField(max_length=15, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"Profile for {self.user.username}"

class PasswordReset(models.Model):
    """
    Models to handel password reset
    """

    # Link to user.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_resets')
    
    # Reset code (6 digit)
    reset_code = models.CharField(max_length=6)
     
    # Phone number (for verification)
    phone_number = models.CharField(max_length=15)

    # Tracking fields
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    #Request Metadata
    ip_address = models.GenericIPAddressField(null=True,blank=True)

    class Meta:
        db_table = 'password_resets'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        #Auto generate reset code
        if not self.reset_code:
            self.reset_code = self.generate_reset_code()

        # Set expiry time 
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=15)

        super().save(*args, **kwargs)

    @staticmethod
    def generate_reset_code():
        """Generating a secure 6 digit reset code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_expired(self):
        """Checking if the reset code is expired"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """check if the code is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()
    
    def mark_as_used(self):
        """Mark the reset code as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Password reset for {self.phone_number} - {self.reset_code}"

# Create your models here.
