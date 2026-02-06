
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import CustomUser
from restaurants.models import Restaurant

class LikedRestaurantListTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(phone_number='+998901234567', password='password123')
        self.client.force_authenticate(user=self.user)
        self.restaurant1 = Restaurant.objects.create(name="Pizza Place")
        self.restaurant2 = Restaurant.objects.create(name="Burger Joint")
        
        # Like restaurant 1
        self.user.liked_restaurants.add(self.restaurant1)
        self.url = reverse('liked-restaurant-list')

    def test_get_liked_restaurants(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should contain one restaurant
        self.assertEqual(len(response.data), 1)
        # The restaurant should be restaurant1
        self.assertEqual(response.data[0]['name'], "Pizza Place")
        self.assertEqual(str(response.data[0]['id']), str(self.restaurant1.id))
