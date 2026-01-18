#type:ignore
import requests
import logging
# from django.conf import settings
from .models import Payment

# logger = logging.getLogger('payments')

logger = logging.getLogger(__name__)

def initiate_uropay_order(order, user,):
    """
    Hardcoded Header version with NGROK Callback.
    Target: https://api.uropay.me/order/generate
    """
    endpoint_url = "https://api.uropay.me/order/generate"

    # YOUR NGROK URL
    BASE_URL = "https://proannexation-wavily-tamela.ngrok-free.dev"

    # Using the exact Bearer token from your curl command
    HARDCODED_AUTH = "Bearer 06a32a99c61b1da483f605f44608470db9ccdd510c41d8d29f16c66d9b69b2ee389876414fea0c05390d41167581f440aaaadc1fb3e87b2f3cc590b77d729adb"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-API-KEY": "5XV9L8GS49Y8FJ43",
        "Authorization": HARDCODED_AUTH
    }

    payload = {
        "vpa": '7261839405@naviaxis',
        "vpaName": 'Kushagra Agarwal',
        "amount": int(order.total_amount * 100),
        "merchantOrderId": str(order.order_id),
        "transactionNote": f"Order {order.order_id}",
        "customerName": f"{user.first_name} {user.last_name}".strip() or user.username,
        "customerEmail": user.email,
        # PRD Section 17: Implementing the Webhook link
        "callback_url": f"{BASE_URL}/payments/webhook/",
        "notes": {
            "order_id": str(order.id)
        }
    }

    try:
        logger.info(f"PAYMENT_INIT: Calling UroPay for Order {order.order_id}")
        response = requests.post(endpoint_url, json=payload, headers=headers, timeout=15)
        logger.info(f"PAYMENT_GATEWAY_RESPONSE: Received URL for Transaction {order.order_id}")

        if response.status_code in [200, 201]:
            data = response.json()
            # print(data)
            Payment.objects.create(
                order=order,
                amount=order.total_amount,
                # transaction_id=data.get('uropayOrderId', 'pending_id'),
                transaction_id=data.get('uropayOrderId'),
                status='pending'
            )
            return data
        else:
            logger.error(f"UroPay Error: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"UroPay Request Failed: {e}")
        return None