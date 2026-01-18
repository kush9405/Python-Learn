#type:ignore
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # 1. Dashboard Columns
    list_display = ('id', 'order_link', 'amount', 'status', 'transaction_id', 'created_at')

    # 2. Filters: Easily find 'Failed' payments
    list_filter = ('status', 'provider', 'created_at')

    # 3. Search: Find by UroPay Transaction ID or Internal Order ID
    search_fields = ('transaction_id', 'order__order_id', 'order__user__username')

    # 4. Security: Prevent Admins from manually changing amounts or IDs
    readonly_fields = ('transaction_id', 'amount', 'order', 'created_at')

    # 5. Helper method to link directly to the Order from the Payment page
    def order_link(self, obj):
        url = reverse("admin:orders_order_change", args=[obj.order.id])
        return format_html('<a href="{}">Order #{}</a>', url, obj.order.order_id)

    order_link.short_description = 'Linked Order'