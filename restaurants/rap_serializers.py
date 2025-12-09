from rest_framework import serializers
from accounts.models import CustomUser
from restaurants.models import Restaurant, RestaurantImage, Cashier

# User with transaction aggregations
class RestaurantUserSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
    total_transactions = serializers.IntegerField()
    total_spent_before_discount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_discount_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_spent_after_discount = serializers.DecimalField(max_digits=12, decimal_places=2)
    last_transaction_date = serializers.DateTimeField()

# Cashier serializers
class CashierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cashier
        fields = ['id', 'name', 'phone_number', 'is_active', 'created_at']

class CashierUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cashier
        fields = ['name', 'phone_number', 'is_active']

# Restaurant settings
class RestaurantImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantImage
        fields = ['id', 'image']

class RestaurantSettingsSerializer(serializers.ModelSerializer):
    gallery = RestaurantImageUploadSerializer(many=True, read_only=True)
    
    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'logo', 'gallery', 'description', 
            'hashtags', 'working_hours', 'contact_information',
            'social_media', 'menu', 'location_text', 'discount_percentage'
        ]
        read_only_fields = ['id']
