#type:ignore
import logging
from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from .models import Notification

logger = logging.getLogger(__name__)


def create_notification_record(user, order, notification_type='email'):
    """
    Service function to create notification tracking record.

    Args:
        user: User object
        order: Order object
        notification_type: Type of notification (email, sms, etc.)

    Returns:
        Notification instance

    Raises:
        ValueError: If user or order is None/invalid
    """
    # Validate inputs before creating
    if not user:
        raise ValueError("User object cannot be None")
    if not order:
        raise ValueError("Order object cannot be None")
    if not hasattr(user, 'email') or not user.email:
        raise ValueError("User must have a valid email address")
    if not hasattr(order, 'order_id'):
        raise ValueError("Order must have an order_id")

    return Notification.objects.create(
        user=user,
        order=order,
        notification_type=notification_type,
        recipient=user.email,
        status='pending',
        message=f"Order {order.order_id} confirmation"
    )


def send_order_confirmation_email(order):
    """
    Service function to send order confirmation email to user.

    Args:
        order: Order instance

    Raises:
        Exception: If email sending fails

    Returns:
        bool: True if email sent successfully
    """
    subject = f"Order Confirmation - {order.order_id}"
    message = f"Hi {order.user.username}, your order for total {order.total_amount} was placed successfully!"

    try:
        django_send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=False,
        )
        logger.info(f"Email successfully sent to {order.user.email}")
        return True
    except Exception as exc:
        logger.error(f"Failed to send email to {order.user.email}: {str(exc)}")
        raise


def update_notification_status(notification, status, error_log=None):
    """
    Service function to update notification status.

    Args:
        notification: Notification instance
        status: New status (pending, sent, failed, permanent_failure)
        error_log: Optional error message
    """
    notification.status = status
    if error_log:
        notification.error_log = error_log
    notification.save()
    logger.info(f"Notification {notification.id} status updated to {status}")