from django.contrib import admin
from .models import Restaurant, RestaurantImage, Cashier

class RestaurantImageInline(admin.TabularInline):
    model = RestaurantImage
    extra = 1

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_text', 'discount_percentage', 'created_at')
    search_fields = ('name', 'hashtags')
    inlines = [RestaurantImageInline]

@admin.register(Cashier)
class CashierAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'phone_number', 'is_active')
    list_filter = ('restaurant', 'is_active')
    search_fields = ('name', 'phone_number')
