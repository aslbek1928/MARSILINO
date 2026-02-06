from django.contrib import admin
from .models import Restaurant, RestaurantImage, Cashier, MenuImage, BookTable

class RestaurantImageInline(admin.TabularInline):
    model = RestaurantImage
    extra = 1

class MenuImageInline(admin.TabularInline):
    model = MenuImage
    extra = 1

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_text', 'discount_percentage', 'created_at')
    search_fields = ('name', 'hashtags')
    inlines = [RestaurantImageInline, MenuImageInline]

@admin.register(Cashier)
class CashierAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'phone_number', 'is_active')
    list_filter = ('restaurant', 'is_active')
    search_fields = ('name', 'phone_number')

@admin.register(BookTable)
class BookTableAdmin(admin.ModelAdmin):
    list_display = ('BTID', 'restaurant', 'user', 'date', 'time', 'number_of_people')
    list_filter = ('restaurant', 'date')
    search_fields = ('user__phone_number', 'restaurant__name')
