import os
import django
from django.contrib.auth import get_user_model

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discount_app.settings')
django.setup()

def create_superuser():
    User = get_user_model()
    phone_number = '+998906100908' # Updated per user request
    password = 'aslbek10.09.2008'

    if not User.objects.filter(phone_number=phone_number).exists():
        print(f"Creating superuser '{phone_number}'...")
        User.objects.create_superuser(phone_number=phone_number, password=password)
        print(f"✅ Superuser '{phone_number}' created successfully!")
    else:
        print(f"ℹ️  Superuser '{phone_number}' already exists.")

if __name__ == "__main__":
    create_superuser()
