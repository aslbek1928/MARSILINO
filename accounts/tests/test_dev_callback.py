from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import CustomUser, PhoneOTP
from accounts.services import OTPService
import time

class DevCallbackTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.phone_number = "+998991234567"
        self.url = reverse('dev-callback')

    def test_callback_new_user(self):
        """Test callback works for a phone number without a user account"""
        # Generate OTP
        OTPService.generate_otp(self.phone_number)
        
        # Call dev-callback
        response = self.client.get(self.url, {'phone_number': self.phone_number})
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['user_id'])
        self.assertEqual(response.data['phone_number'], self.phone_number)
        self.assertTrue('code' in response.data)

    def test_callback_existing_user(self):
        """Test callback works for an existing user"""
        user = CustomUser.objects.create(phone_number=self.phone_number)
        
        # Generate OTP
        # Wait a bit or clear old OTPs if rate limiting is an issue, 
        # but in tests usually irrelevant unless checking limits explicitly.
        # However, OTPService has rate limiting.
        # Let's direct create PhoneOTP to avoid rate limit logic complications in test if run sequentially quickly,
        # or just mock time. But simplified:
        PhoneOTP.objects.filter(phone_number=self.phone_number).delete()
        OTPService.generate_otp(self.phone_number)

        response = self.client.get(self.url, {'phone_number': self.phone_number})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data['user_id']), str(user.id))
        self.assertEqual(response.data['phone_number'], self.phone_number)

    def test_callback_no_otp(self):
        """Test callback fails if no OTP exists"""
        response = self.client.get(self.url, {'phone_number': "+998999999999"})
        self.assertEqual(response.status_code, 404)
