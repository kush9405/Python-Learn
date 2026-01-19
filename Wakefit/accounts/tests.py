from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountValidationTest(APITestCase):
    def test_duplicate_username_registration(self):
        """Verify registration fails for existing usernames."""
        User.objects.create_user(username="Sanjeev", email="test@test.com", password="pass")

        payload = {
            "username": "Sanjeev",
            "email": "new@test.com",
            "password": "newpassword123"
        }
        response = self.client.post(reverse('auth_register'), payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)