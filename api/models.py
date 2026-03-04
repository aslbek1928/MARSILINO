from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractUser):
    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('ru', 'Russian'),
        ('uz', 'Uzbek'),
    )
    username = None  # Remove username field
    phone_number = models.CharField(_("phone number"), max_length=20, unique=True)
    full_name = models.CharField(_("full name"), max_length=255, blank=True)
    wallet_balance = models.DecimalField(_("wallet balance"), max_digits=12, decimal_places=2, default=0.00)
    language = models.CharField(
        max_length=2, 
        choices=LANGUAGE_CHOICES, 
        default='ru',
        verbose_name=_("language preference")
    )
    liked_restaurants = models.ManyToManyField('Restaurant', related_name='liked_by', blank=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.phone_number} ({self.full_name or 'No Name'})"


class FCMDevice(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='fcm_devices')
    fcm_token = models.TextField(unique=True)
    device_type = models.CharField(max_length=20, choices=(('ios', 'iOS'), ('android', 'Android')))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_type} token for {self.user.phone_number}"


class Tag(models.Model):
    id = models.CharField(max_length=50, primary_key=True)  # e.g., "tag_1", "halal"
    name = models.CharField(_("name"), max_length=100)
    icon_url = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    id = models.CharField(max_length=100, primary_key=True)  # e.g., "rest_123"
    tin = models.CharField(_("tax identification number (TIN)"), max_length=20, unique=True)
    name = models.CharField(_("name"), max_length=200)
    description = models.TextField(_("description"), blank=True)
    cashback_percentage = models.DecimalField(_("cashback percentage"), max_digits=5, decimal_places=2, default=5.0)
    tags = models.ManyToManyField(Tag, related_name='restaurants', blank=True)
    logo = models.ImageField(_("logo"), upload_to='restaurant_logos/', null=True, blank=True)
    menu = models.ImageField(_("menu"), upload_to='restaurant_menus/', null=True, blank=True)
    location_link = models.URLField(_("location link"), max_length=500, blank=True)
    contact = models.CharField(_("contact number"), max_length=50, blank=True)
    working_days_and_hours = models.CharField(_("working days and hours"), max_length=200, blank=True)
    location_description_en = models.TextField(_("location description (EN)"), blank=True)
    location_description_ru = models.TextField(_("location description (RU)"), blank=True)
    location_description_uz = models.TextField(_("location description (UZ)"), blank=True)

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            total = sum(review.rating for review in reviews)
            return round(total / reviews.count(), 1)
        return 0.0

    @property
    def total_reviews(self):
        return self.reviews.count()

    def __str__(self):
        return self.name


class RestaurantImage(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='media')
    image = models.ImageField(_("image"), upload_to='restaurant_media/')

    def __str__(self):
        return f"Image for {self.restaurant.name}"



class RedeemedReceipt(models.Model):
    receipt_id = models.CharField(max_length=100, unique=True)
    receipt_number = models.CharField(max_length=50)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='redeemed_receipts')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='redeemed_receipts')
    total_paid = models.DecimalField(max_digits=12, decimal_places=2)
    cashback_amount = models.DecimalField(max_digits=12, decimal_places=2)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt {self.receipt_id} for {self.user.phone_number}"


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('cashback_add', 'Cashback Add'),
        ('transfer_out', 'Transfer Out'),
    )

    TRANSACTION_STATUSES = (
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    )

    transaction_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wallet_transactions')
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    receipt_id = models.CharField(max_length=100, null=True, blank=True)
    restaurant_id = models.CharField(max_length=100, null=True, blank=True)
    card_last_four = models.CharField(max_length=4, null=True, blank=True)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUSES, default='completed')
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.type} of {self.amount} for {self.user.phone_number}"


class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps', null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP {self.code} for {self.phone_number}"

from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("rating (1-5)")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'restaurant')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.phone_number} rated {self.restaurant.name} {self.rating}/5"
