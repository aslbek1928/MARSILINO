import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework.test import APIClient
from api.models import CustomUser

client = APIClient()

# Set user's language preference to 'uz'
user = CustomUser.objects.get(phone_number='+998906100908')
user.language = 'uz'
user.save()

# Login
response = client.post('/api/token/', {'phone_number': '+998906100908', 'password': 'Aslbek@10.09.2008'})
assert response.status_code == 200, f"Login failed: {response.data}"
token = response.data['access']
client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

# Test Tags Locale - Should default to 'uz' because of the user's preference, 
# even WITHOUT the Accept-Language header.
response = client.get('/api/v1/tags')
assert response.status_code == 200
assert response.data['data'][0]['name'] == 'Halol', f"Expected Halol, got {response.data}"

# Change user preference to 'ru' and test again
user.language = 'ru'
user.save()

response = client.get('/api/v1/tags')
assert response.status_code == 200
assert response.data['data'][0]['name'] == 'Халяль', f"Expected Халяль, got {response.data}"

# Test MeView update language to 'en'
response = client.patch('/api/v1/me', {'language': 'en'})
assert response.status_code == 200
assert response.data['data']['language'] == 'en'

# Verify tags locale is now English
response = client.get('/api/v1/tags')
assert response.status_code == 200
assert response.data['data'][0]['name'] == 'Halal', f"Expected Halal, got {response.data}"

print("LANGUAGE PREFERENCE TESTS PASSED!")
