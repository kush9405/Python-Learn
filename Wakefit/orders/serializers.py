# type:ignore
# orders/serializers.py
from products.serializers import ProductMinimalSerializer  # Import the new one
from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class OrderCreateSerializer(serializers.Serializer):
    address = serializers.CharField(
        style={'base_template': 'textarea.html'},
        help_text="Enter your full delivery address"
    )
    # vpa = serializers.CharField(label="UPI ID")
    # vpa_name = serializers.CharField(label="Name on UPI")

    # --- FOR THE HTML FORM (Single Item Convenience) ---
    product_id = serializers.IntegerField(required=False, write_only=True, help_text="Used for single item orders")
    quantity = serializers.IntegerField(required=False, write_only=True, min_value=1)

    # --- FOR THE RAW DATA (Multiple Items Support) ---
    items = OrderItemSerializer(many=True, required=False)

    def validate(self, data):
        """
        PRD Section 11: Validation logic.
        Ensures that if 'items' is missing, 'product_id' and 'quantity' are present.
        """
        items = data.get('items')
        p_id = data.get('product_id')
        qty = data.get('quantity')

        if not items and not (p_id and qty):
            raise serializers.ValidationError("You must provide at least one product.")
        
        return data
    



class OrderItemReadSerializer(serializers.ModelSerializer):
    # Use the Minimal Serializer here
    product = ProductMinimalSerializer(read_only=True)

    class Meta:
        model = OrderItem
        # 'price' here is the price-at-purchase, 'quantity' is how many they bought.
        fields = ['product', 'quantity', 'price']

class OrderHistorySerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'total_amount', 'status', 'address', 'created_at', 'items']