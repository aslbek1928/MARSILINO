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
    wallet_balance = models.DecimalField(_("wallet balance"), max_digits=12, decimal_places=2, default=0.00)
    language = models.CharField(
        max_length=2, 
        choices=LANGUAGE_CHOICES, 
        default='ru',
        verbose_name=_("language preference")
    )

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.phone_number} (Bal: {self.wallet_balance})"


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

    def __str__(self):
        return self.name


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
