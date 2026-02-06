from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from core.models import TimeStampedModel
import secrets

class Restaurant(TimeStampedModel):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='restaurant_logos/', blank=True, null=True)
    # gallery handled by RestaurantImage model
    description = models.TextField(blank=True)
    hashtags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")
    working_hours = models.TextField(blank=True)
    contact_information = models.TextField(blank=True)
    social_media = models.JSONField(default=dict, blank=True)
    menu = models.JSONField(default=list, blank=True)
    location_text = models.TextField(blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

class RestaurantImage(TimeStampedModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='restaurant_gallery/')

    def __str__(self):
        return f"Image for {self.restaurant.name}"

class Cashier(TimeStampedModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='cashiers')
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    pin_code = models.CharField(max_length=255)  # Stored as hash
    is_active = models.BooleanField(default=True)

    def set_pin(self, raw_pin):
        """Hash and store the PIN"""
        self.pin_code = make_password(raw_pin)
    
    def check_pin(self, raw_pin):
        """Verify a PIN against the stored hash"""
        return check_password(raw_pin, self.pin_code)
    
    @staticmethod
    def generate_pin(length=4):
        """Generate a random numeric PIN"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

class MenuImage(TimeStampedModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_images')
    image = models.ImageField(upload_to='restaurant_menu/')
    order = models.PositiveIntegerField(default=0, help_text="Display order of menu pages")

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Menu Page {self.order} for {self.restaurant.name}"


class BookTable(models.Model):
    BTID = models.AutoField(primary_key=True)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='bookings')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='bookings')
    customer_phone_number = models.CharField(max_length=20)
    number_of_people = models.PositiveIntegerField()
    date = models.DateField()
    time = models.TimeField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.BTID} at {self.restaurant.name} by {self.user.phone_number}"
