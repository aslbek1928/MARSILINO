from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PhoneOTP, RestaurantAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    ordering = ('phone_number',)
    list_display = ('phone_number', 'full_name', 'is_staff', 'is_active')
    search_fields = ('phone_number', 'full_name')
    list_filter = ('is_staff', 'is_active')
    
    # Important: Override these to remove 'username' references
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Liked Restaurants', {'fields': ('liked_restaurants',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # This is critical: defines fields when ADDING a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'full_name', 'is_staff', 'is_active'),
        }),
    )
    
    # Override filter_horizontal for liked_restaurants
    filter_horizontal = ('liked_restaurants', 'groups', 'user_permissions')
    readonly_fields = ('date_joined', 'last_login')

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'created_at', 'expires_at', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('phone_number',)

@admin.register(RestaurantAdmin)
class RestaurantAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant')
    search_fields = ('user__phone_number', 'restaurant__name')

