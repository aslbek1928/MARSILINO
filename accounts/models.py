from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from core.models import TimeStampedModel
import uuid
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number=None, email=None, password=None, **extra_fields):
        if not phone_number and not email:
            raise ValueError('Either Phone Number or Email must be set')
        
        if email:
            email = self.normalize_email(email)
        
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    liked_restaurants = models.ManyToManyField('restaurants.Restaurant', blank=True, related_name='liked_by_users')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.phone_number or self.email or f"User {self.id}"

class PhoneOTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    attempt_count = models.IntegerField(default=0)

    def __str__(self):
        return f"OTP for {self.phone_number}"

class RestaurantAdmin(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='restaurant_admin_profile')
    restaurant = models.OneToOneField('restaurants.Restaurant', on_delete=models.CASCADE, related_name='admin_profile')

    def __str__(self):
        return f"Admin for {self.restaurant}"
