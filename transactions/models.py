from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class Transaction(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE, related_name='transactions')
    cashier = models.ForeignKey('restaurants.Cashier', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    
    sum_before_discount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    sum_after_discount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount_uzs = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Transaction {self.id} - {self.user} at {self.restaurant}"
