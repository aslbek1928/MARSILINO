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
    user_id = serializers.UUIDField(allow_null=True)
    phone_number = serializers.CharField()
    code = serializers.CharField()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'full_name', 'email', 'password']
        extra_kwargs = {
            'full_name': {'required': False},
            'email': {'required': False}
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            phone_number=validated_data['phone_number'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            full_name=validated_data.get('full_name', '')
        )
        return user
