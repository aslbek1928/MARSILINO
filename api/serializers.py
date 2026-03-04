from rest_framework import serializers
from .models import Tag, Restaurant, CustomUser, WalletTransaction, FCMDevice, OTP, RestaurantImage, Review

class OTPSendSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)

class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)
    full_name = serializers.CharField(max_length=255, required=False, allow_blank=True)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

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
    average_rating = serializers.FloatField(read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'description', 'tin', 'cashback_percentage', 
            'tags', 'is_liked', 'logo', 'menu', 'location_link', 'media',
            'contact', 'working_days_and_hours', 'average_rating', 'total_reviews',
            'reviews', 'location_description_en', 'location_description_ru', 
            'location_description_uz'
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
