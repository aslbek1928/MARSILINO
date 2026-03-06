from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class UserCardUpdateTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="+998901112233", password="testpassword")

    def test_update_card_via_get(self):
        card_num = "8600000011112222"
        response = self.client.get(reverse('user-card-update'), {
            'phone_number': '+998901112233',
            'card_number': card_num
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['card_number'], card_num)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.card_number, card_num)

    def test_update_card_invalid_length(self):
        card_num = "123" # too short
        response = self.client.get(reverse('user-card-update'), {
            'phone_number': '+998901112233',
            'card_number': card_num
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_update_card_user_not_found(self):
        response = self.client.get(reverse('user-card-update'), {
            'phone_number': '+998900000000',
            'card_number': "8600000011112222"
        })
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()['success'])
