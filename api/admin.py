from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import CustomUser, Tag, Restaurant, RedeemedReceipt, WalletTransaction, RestaurantImage, Review

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'wallet_balance', 'is_staff', 'is_active')
    search_fields = ('phone_number',)

@admin.register(Tag)
class TagAdmin(TranslationAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')

class RestaurantImageInline(admin.TabularInline):
    model = RestaurantImage
    extra = 1

@admin.register(Restaurant)
class RestaurantAdmin(TranslationAdmin):
    list_display = ('id', 'name', 'tin', 'cashback_percentage', 'average_rating', 'total_reviews')
    search_fields = ('id', 'name', 'tin')
    filter_horizontal = ('tags',)
    inlines = [RestaurantImageInline]

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

from .models import OTP
@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'created_at', 'is_verified')
    search_fields = ('phone_number', 'code')
    list_filter = ('is_verified', 'created_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'restaurant')
    search_fields = ('user__phone_number', 'restaurant__name')
