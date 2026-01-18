#type:ignore
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from products.models import Product
from orders.models import Order, OrderItem
from payments.models import Payment

User = get_user_model()

class EndToEndOrderFlowTest(APITestCase):

    def setUp(self):
        """
        Setup data needed for every test.
        """
        # Create a product in the 'Master Data' table
        self.product = Product.objects.create(
            name="Test Mattress",
            sku="WK-001",
            price=5000.00,
            stock_quantity=10,
            is_active=True
        )
        self.register_url = reverse('auth_register') # Ensure this name matches your urls.py
        self.login_url = reverse('token_obtain_pair')
        self.order_url = reverse('place_order')

    def test_complete_user_journey(self):
        """
        PRD Section 19: Functional Requirements Check.
        Flow: Register -> Login -> Place Order -> Mock Payment API
        """
        
        # --- STEP 1: USER REGISTRATION ---
        user_data = {
            "username": "tester",
            "email": "tester@example.com",
            "password": "SecurePassword123"
        }
        response = self.client.post(self.register_url, user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        # --- STEP 2: LOGIN & GET JWT TOKEN ---
        login_data = {
            "username": "tester",
            "password": "SecurePassword123"
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']
        
        # Authenticate the 'Postman' client for subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # --- STEP 3: PLACE ORDER (With Payment Mocking) ---
        # We 'patch' the UroPay API call so we don't hit the real internet
        with patch('payments.services.requests.post') as mock_uropay:
            # Setup the 'Fake' response from UroPay
            mock_uropay.return_value.status_code = 200
            mock_uropay.return_value.json.return_value = {
                "uropayOrderId": "URO_MOCK_12345",
                "payment_url": "https://test.uropay.me/pay/mock"
            }

            order_payload = {
                "address": "456 Backend Lane, Python City",
                "product_id": self.product.id,
                "quantity": 2,
            }

            response = self.client.post(self.order_url, order_payload, format='json')

            # --- VERIFICATIONS ---
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            # 1. Check if Order exists in DB
            self.assertEqual(Order.objects.count(), 1)
            order = Order.objects.first()
            self.assertEqual(order.address, "456 Backend Lane, Python City")

            # 2. Check PRD Section 9: Stock reduction
            self.product.refresh_from_db()
            self.assertEqual(self.product.stock_quantity, 8) # 10 - 2 = 8

            # 3. Check PRD Section 8: Payment record creation
            self.assertEqual(Payment.objects.count(), 1)
            payment = Payment.objects.first()
            self.assertEqual(payment.transaction_id, "URO_MOCK_12345")

    def test_stock_protection_logic(self):
        """
        Verify that a user cannot buy more than available stock.
        """
        # Create user and auth
        user = User.objects.create_user(username="buyer", password="password")
        self.client.force_authenticate(user=user)

        bad_payload = {
            "address": "Test",
            "product_id": self.product.id,
            "quantity": 99, # More than 10 in stock
        }

        response = self.client.post(self.order_url, bad_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Not enough stock", str(response.data))