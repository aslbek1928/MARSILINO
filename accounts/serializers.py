from rest_framework import serializers
from .models import CustomUser, RestaurantAdmin

class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)

class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'phone_number', 'full_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    """For GET/PATCH /api/me/"""
    liked_restaurants = serializers.PrimaryKeyRelatedField(
        many=True, 
        read_only=True
    )
    
    class Meta:
        model = CustomUser
        fields = ['id', 'phone_number', 'full_name', 'liked_restaurants', 'date_joined']
        read_only_fields = ['id', 'phone_number', 'liked_restaurants', 'date_joined']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """For PATCH /api/me/ - allows updating full_name"""
    class Meta:
        model = CustomUser
        fields = ['full_name']

class RestaurantAdminLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)


class DevCallbackSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    phone_number = serializers.CharField()
    code = serializers.CharField()
