
from django.test import TestCase
from django.urls import reverse

class HomepageTests(TestCase):
    def test_homepage_status_code(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_homepage_contains_correct_content(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, "Marsilino")
        self.assertContains(response, "#BC2749")  # Check for primary color
