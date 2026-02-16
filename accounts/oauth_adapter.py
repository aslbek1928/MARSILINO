from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom adapter for standard account operations"""
    
    def is_open_for_signup(self, request):
        """Allow signups"""
        return True


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter to handle OAuth user creation and authentication"""
    
    def pre_social_login(self, request, sociallogin):
        """
        Handle linking of social account to existing user if email matches
        """
        if sociallogin.is_existing:
            return
        
        # Try to link social account to existing user with same email
        try:
            email = sociallogin.account.extra_data.get('email', '').lower()
            if email:
                from accounts.models import CustomUser
                try:
                    user = CustomUser.objects.get(email=email)
                    sociallogin.connect(request, user)
                except CustomUser.DoesNotExist:
                    pass
        except:
            pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save the user from OAuth data
        """
        user = super().save_user(request, sociallogin, form)
        
        # Extract data from Google OAuth response
        data = sociallogin.account.extra_data
        
        # Update user profile with Google data
        if not user.full_name and 'name' in data:
            user.full_name = data.get('name', '')
        
        user.save()
        
        return user
    
    def populate_user(self, request, sociallogin, data):
        """
        Populate user instance with data from social provider
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Set email from OAuth data
        email = data.get('email', '').lower()
        if email:
            user.email = email
        
        # Set full name from OAuth data
        if 'name' in data:
            user.full_name = data.get('name', '')
        
        return user
