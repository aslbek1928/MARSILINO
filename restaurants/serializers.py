from rest_framework import serializers
from .models import Restaurant, RestaurantImage, Cashier, MenuImage, BookTable

class BookTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookTable
        fields = ['BTID', 'user', 'restaurant', 'customer_phone_number', 'number_of_people', 'date', 'time', 'comment']
        read_only_fields = ['BTID', 'user']


class RestaurantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantImage
        fields = ['id', 'image']

class MenuImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuImage
        fields = ['id', 'image', 'order']

class RestaurantListSerializer(serializers.ModelSerializer):
    """Basic info for list view"""
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'logo', 'hashtags', 'location_text', 'discount_percentage']

class RestaurantDetailSerializer(serializers.ModelSerializer):
    """Full info for detail view"""
    gallery = RestaurantImageSerializer(many=True, read_only=True)
    menu_images = MenuImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'logo', 'gallery', 'description', 
            'hashtags', 'working_hours', 'contact_information',
            'social_media', 'menu', 'menu_images', 'location_text', 'discount_percentage',
            'created_at', 'updated_at'
        ]

# Cashier Serializers
class CashierLoginSerializer(serializers.Serializer):
    restaurant_id = serializers.UUIDField()
    phone_number = serializers.CharField(max_length=20)
    pin_code = serializers.CharField(max_length=10)

class CashierInfoSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    
    class Meta:
        model = Cashier
        fields = ['id', 'name', 'phone_number', 'restaurant', 'restaurant_name', 'is_active']

class CashierCreateSerializer(serializers.ModelSerializer):
    """For creating a new cashier (admin only)"""
    class Meta:
        model = Cashier
        fields = ['id', 'restaurant', 'name', 'phone_number']
        read_only_fields = ['id']

class CashierPINResetSerializer(serializers.Serializer):
    cashier_id = serializers.UUIDField()

