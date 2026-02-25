from rest_framework import serializers
from .models import Tag, Restaurant

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'icon_url']

class RestaurantSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'description', 'tin', 'cashback_percentage', 'tags']

from .models import CustomUser

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'phone_number', 'wallet_balance', 'language']
        read_only_fields = ['id', 'phone_number', 'wallet_balance']
