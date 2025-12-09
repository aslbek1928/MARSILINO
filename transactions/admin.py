from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'restaurant', 'sum_after_discount', 'created_at')
    list_filter = ('restaurant', 'created_at')
    search_fields = ('user__phone_number', 'restaurant__name')
    readonly_fields = ('created_at', 'updated_at')
