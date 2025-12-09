from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    cashier_name = serializers.CharField(source='cashier.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'restaurant', 'restaurant_name', 'cashier', 'cashier_name',
            'sum_before_discount', 'discount_percentage', 
            'sum_after_discount', 'discount_amount_uzs', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
