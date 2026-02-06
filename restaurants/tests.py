
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Restaurant, BookTable
from accounts.models import CustomUser

class BookTableAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(phone_number='+998901234567', password='password123')
        self.client.force_authenticate(user=self.user)
        self.restaurant = Restaurant.objects.create(name="Test Restaurant")
        self.url = reverse('book-table')

    def test_create_booking(self):
        data = {
            'restaurant': self.restaurant.id,
            'customer_phone_number': '+998901234567',
            'number_of_people': 4,
            'date': '2026-05-20',
            'time': '19:00',
            'comment': 'Quiet table please'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookTable.objects.count(), 1)
        self.assertEqual(BookTable.objects.get().restaurant.name, "Test Restaurant")
