#type:ignore
import logging
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from orders.models import Order
from .services import (
    create_notification_record,
    send_order_confirmation_email,
    update_notification_status,
)

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
        notif = create_notification_record(order.user, order)

        # 4. Send order confirmation email (extracted to service)
        send_order_confirmation_email(order)

        # 5. Success Path
        update_notification_status(notif, 'sent')
        return f"Email sent to {order.user.email}"

    except Exception as exc:
        # 6. Error Handling with Exponential Backoff (Section 11 & 16)
        logger.error(f"Task failed for Order {order_id}: {str(exc)}")

        if notif:
            update_notification_status(notif, 'failed', error_log=str(exc))

        # Exponential retry: 2^retry_count minutes
        # Retry 1: 2^1 = 2 minutes (120 seconds)
        # Retry 2: 2^2 = 4 minutes (240 seconds)
        # Retry 3: 2^3 = 8 minutes (480 seconds)
        countdown = 60 * (2 ** self.request.retries)

        try:
            logger.warning(f"Retrying task for Order {order_id} in {countdown}s (Attempt {self.request.retries + 1}/3)")
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            logger.critical(f"Max retries exceeded for Order {order_id}. Email delivery failed permanently.")
            if notif:
                update_notification_status(notif, 'permanent_failure')