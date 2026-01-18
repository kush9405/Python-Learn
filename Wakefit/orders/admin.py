from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 # Prevents empty rows from appearing
    # Make product and price read-only to prevent accidental data changes
    readonly_fields = ('product', 'price', 'quantity')
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # 1. Dashboard Columns
    list_display = ('order_id', 'user', 'total_amount', 'status', 'created_at')
    
    # 2. PRD Section 14: Sidebar Filters
    list_filter = ('status', 'created_at')
    
    # 3. Search Functionality
    search_fields = ('order_id', 'user__username', 'user__email', 'address')
    
    # 4. Inlines: See items inside the order
    inlines = [OrderItemInline]

    # 5. Data Integrity: Keep sensitive fields read-only
    readonly_fields = ('order_id', 'user', 'total_amount', 'created_at', 'updated_at')

    # 6. Organization: Split the view into sections
    fieldsets = (
        ('Order Info', {
            'fields': ('order_id', 'user', 'status')
        }),
        ('Billing & Shipping', {
            'fields': ('total_amount', 'address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )