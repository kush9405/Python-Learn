from rest_framework.test import APITestCase
from django.urls import reverse
from orders.models import Order
from payments.models import Payment
from django.contrib.auth import get_user_model

User = get_user_model()

class PaymentWebhookTest(APITestCase):
    def test_uropay_webhook_updates_order(self):
        """PRD Section 17: Verify automated order status update via Webhook."""
        # 1. Setup Pending Order
        user = User.objects.create_user(username="paytester", password="password")
        order = Order.objects.create(user=user, total_amount=1000, status='pending')
        Payment.objects.create(order=order, amount=1000, transaction_id="URO_123", status='pending')

        # 2. Mock Webhook Payload from UroPay
        webhook_data = {
            "merchantOrderId": str(order.order_id),
            "status": "SUCCESS",
            "transaction_id": "URO_123"
        }

        # 3. Post to Webhook (Unauthenticated, as it comes from UroPay)
        url = reverse('uropay_webhook')
        response = self.client.post(url, webhook_data, format='json')

        # 4. Verify Success
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, 'paid')