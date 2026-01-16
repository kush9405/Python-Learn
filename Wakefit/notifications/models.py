from django.db import models
from django.conf import settings
from orders.models import Order

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('email', 'Email'),
        ('sms', 'SMS'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    # Optional: Link to an order if the notification is order-related
    order = models.ForeignKey(
        Order, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    recipient = models.CharField(max_length=255)  # Email address or Phone number
    message = models.TextField()
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Section 16: For retries and idempotency
    retry_count = models.IntegerField(default=0)
    error_log = models.TextField(null=True, blank=True) # To store why it failed
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.notification_type} to {self.recipient} - {self.status}"