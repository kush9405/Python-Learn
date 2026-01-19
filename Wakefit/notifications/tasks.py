#type:ignore
import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from orders.models import Order
from .models import Notification

# Setup logging as per PRD Section 6
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_order_confirmation_task(self, order_id):
    """
    Background task to send order confirmation email.
    Follows PRD Section 16 (Retries) and Section 17 (3rd Party Mocking).
    """
    # 1. Local Model Imports (Prevents circular import/registry errors in Celery)

    # 2. Initialize notif inside the function scope
    notif = None

    try:
        # Fetch the order
        order = Order.objects.get(id=order_id)

        # 3. Create the tracking record (Initial status: pending)
        notif = Notification.objects.create(
            user=order.user,
            order=order,
            notification_type='email',
            recipient=order.user.email,
            status='pending',
            message=f"Order {order.order_id} confirmation"
        )

        # 4. Attempt to send real email
        subject = f"Order Confirmation - {order.order_id}"
        message = f"Hi {order.user.username}, your order for total {order.total_amount} was placed successfully!"

        # Note: Use DEFAULT_FROM_EMAIL from your settings.py
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=False,
        )

        # 5. Success Path
        notif.status = 'sent'
        notif.save()
        logger.info(f"Email successfully sent to {order.user.email}")
        return f"Email sent to {order.user.email}"

    except Exception as exc:
        # 6. Error Handling (Section 11 & 16)
        logger.error(f"Task failed for Order {order_id}: {str(exc)}")

        if notif:
            notif.status = 'failed'
            notif.error_log = str(exc)
            notif.save()

        # Trigger Celery Retry logic
        raise self.retry(exc=exc, countdown=60)