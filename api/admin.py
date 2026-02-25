from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import CustomUser, Tag, Restaurant, RedeemedReceipt, WalletTransaction

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'wallet_balance', 'is_staff', 'is_active')
    search_fields = ('phone_number',)

@admin.register(Tag)
class TagAdmin(TranslationAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')

@admin.register(Restaurant)
class RestaurantAdmin(TranslationAdmin):
    list_display = ('id', 'name', 'tin', 'cashback_percentage')
    search_fields = ('id', 'name', 'tin')
    filter_horizontal = ('tags',)

@admin.register(RedeemedReceipt)
class RedeemedReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_id', 'user', 'restaurant', 'total_paid', 'cashback_amount', 'redeemed_at')
    search_fields = ('receipt_id', 'user__phone_number', 'restaurant__name')
    list_filter = ('redeemed_at', 'restaurant')

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'type', 'amount', 'status', 'created_at')
    search_fields = ('transaction_id', 'user__phone_number')
    list_filter = ('type', 'status', 'created_at')
