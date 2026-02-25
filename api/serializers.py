from rest_framework import serializers
from .models import Tag, Restaurant

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'icon_url']

class RestaurantSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'description', 'tin', 'cashback_percentage', 'tags', 'is_liked']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.liked_restaurants.filter(id=obj.id).exists()
        return False

from .models import CustomUser, WalletTransaction, FCMDevice

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
