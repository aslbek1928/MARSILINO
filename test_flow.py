import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework.test import APIClient
from api.models import CustomUser

client = APIClient()

# 1. Login
response = client.post('/api/token/', {'phone_number': '+998901234567', 'password': 'password123'})
assert response.status_code == 200, f"Login failed: {response.data}"
token = response.data['access']
client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

# 2. Test Tags Locale (Uzbek)
response = client.get('/api/v1/tags', HTTP_ACCEPT_LANGUAGE='uz')
assert response.status_code == 200
assert response.data['data'][0]['name'] == 'Halol', f"Expected Halol, got {response.data}"

# 3. Test Restaurants Locale (Russian)
response = client.get('/api/v1/restaurants', HTTP_ACCEPT_LANGUAGE='ru')
assert response.status_code == 200
assert response.data['data'][0]['name'] == 'Тест Рест', f"Expected Тест Рест, got {response.data}"

# 4. Wallet Check
response = client.get('/api/v1/wallet')
assert response.status_code == 200
assert response.data['data']['balance'] == 0.0

# 5. Receipt Verify
# Assuming soliq URL check format
# t = 123456789, r = 1, c = 20250221120000, s = 150000.00
qr_url = "https://ofd.soliq.uz/check?t=123456789&r=1&c=20250221120000&s=150000.00"
response = client.post('/api/v1/receipt/verify', {'qr_code_url': qr_url})
assert response.status_code == 200, f"Verify failed: {response.data}"
assert response.data['data']['cashback_earned'] == 7500.0, f"Expected 7500.0 cashback, got {response.data}"

# 6. Receipt Verify Again (409)
response = client.post('/api/v1/receipt/verify', {'qr_code_url': qr_url})
assert response.status_code == 409, f"Double redemption didn't fail: {response.data}"

# 7. Transfer Out
response = client.post('/api/v1/wallet/transfer', {'amount': 5000.0, 'card_last_four': '1234'})
assert response.status_code == 200, f"Transfer failed: {response.data}"
assert response.data['data']['new_balance'] == 2500.0

# 8. Transfer Out Insufficient (400)
response = client.post('/api/v1/wallet/transfer', {'amount': 3000.0, 'card_last_four': '1234'})
assert response.status_code == 400, f"Insufficient balance check failed: {response.data}"

print("ALL TESTS PASSED!")
