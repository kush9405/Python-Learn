from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    # What columns to show in the list view
    list_display = ('id', 'user', 'notification_type', 'recipient', 'status', 'created_at')
    
    # Add a sidebar to filter by status (Sent/Failed/Pending)
    list_filter = ('status', 'notification_type', 'created_at')
    
    # Allow searching by email or username
    search_fields = ('recipient', 'user__username', 'order__order_id')
    
    # Professional touch: Make these fields read-only in the admin 
    # so admins can't "fake" a sent status manually.
    readonly_fields = ('created_at', 'sent_at', 'retry_count', 'error_log')

    # Grouping fields for a cleaner detail view
    fieldsets = (
        ('Target Info', {
            'fields': ('user', 'order', 'notification_type', 'recipient')
        }),
        ('Status Tracking', {
            'fields': ('status', 'sent_at', 'retry_count', 'error_log')
        }),
        ('Content', {
            'fields': ('message',)
        }),
    )