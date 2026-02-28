from rest_framework import serializers
from .models import Tag, Restaurant, CustomUser, WalletTransaction, FCMDevice, OTP, RestaurantImage

class OTPSendSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)

class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)
    full_name = serializers.CharField(max_length=255, required=False, allow_blank=True)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['phone_number', 'password', 'full_name']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', '')
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'phone_number', 'full_name', 'wallet_balance', 'language']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'icon_url']

class RestaurantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantImage
        fields = ['id', 'image']

class RestaurantSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    media = RestaurantImageSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'description', 'tin', 'cashback_percentage', 
            'tags', 'is_liked', 'logo', 'menu', 'location_link', 'media'
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.liked_restaurants.filter(id=obj.id).exists()
        return False


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'phone_number', 'full_name', 'wallet_balance', 'language']
        read_only_fields = ['id', 'phone_number', 'wallet_balance']

class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = [
            'transaction_id', 'type', 'amount', 'balance_before', 
            'balance_after', 'receipt_id', 'restaurant_id', 
            'card_last_four', 'status', 'created_at'
        ]

class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ['fcm_token', 'device_type', 'created_at']
