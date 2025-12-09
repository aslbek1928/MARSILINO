import random
from django.utils import timezone
from datetime import timedelta
from .models import PhoneOTP
import logging

logger = logging.getLogger(__name__)

class TelegramService:
    @staticmethod
    def send_otp(phone_number, code):
        """
        Sends OTP via Telegram.
        For now, this just logs the code to the console/logger.
        """
        # In production, use python-telegram-bot here
        logger.info(f"----------------------------------------")
        logger.info(f"TELEGRAM OTP for {phone_number}: {code}")
        logger.info(f"----------------------------------------")
        print(f"TELEGRAM OTP for {phone_number}: {code}") # Print to stdout for dev visibility

class OTPService:
    RATE_LIMIT_MINUTES = 1  # Minimum time between OTP requests
    MAX_OTP_PER_HOUR = 5    # Maximum OTPs per hour
    
    @staticmethod
    def generate_otp(phone_number):
        now = timezone.now()
        
        # Rate limiting: Check if recent OTP exists
        recent_otp = PhoneOTP.objects.filter(
            phone_number=phone_number,
            created_at__gt=now - timedelta(minutes=OTPService.RATE_LIMIT_MINUTES)
        ).exists()
        
        if recent_otp:
            raise ValueError("Please wait before requesting another OTP")
        
        # Check hourly limit
        hour_ago = now - timedelta(hours=1)
        hourly_count = PhoneOTP.objects.filter(
            phone_number=phone_number,
            created_at__gt=hour_ago
        ).count()
        
        if hourly_count >= OTPService.MAX_OTP_PER_HOUR:
            raise ValueError("Too many OTP requests. Please try again later.")
        
        # Generate 6-digit code
        code = str(random.randint(100000, 999999))
        expires_at = now + timedelta(minutes=5)
        
        # Create OTP record
        PhoneOTP.objects.create(
            phone_number=phone_number,
            code=code,
            expires_at=expires_at
        )
        
        # Send via Telegram
        TelegramService.send_otp(phone_number, code)
        return code


    @staticmethod
    def verify_otp(phone_number, code):
        now = timezone.now()
        otp_record = PhoneOTP.objects.filter(
            phone_number=phone_number,
            is_verified=False,
            expires_at__gt=now
        ).order_by('-created_at').first()

        if not otp_record:
            return False, "OTP expired or invalid"

        if otp_record.attempt_count >= 3:
            return False, "Too many attempts"

        if otp_record.code != code:
            otp_record.attempt_count += 1
            otp_record.save()
            return False, "Invalid code"

        otp_record.is_verified = True
        otp_record.save()
        return True, "Success"
