# type:ignore
# orders/serializers.py
from products.models import Product
from products.serializers import ProductMinimalSerializer  # Import the new one
from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class OrderCreateSerializer(serializers.Serializer):
    address = serializers.CharField(
        style={'base_template': 'textarea.html'},
        help_text="Enter your full delivery address",
        min_length=5, max_length=500
    )
    # vpa = serializers.CharField(label="UPI ID")
    # vpa_name = serializers.CharField(label="Name on UPI")

    # --- FOR THE HTML FORM (Single Item Convenience) ---
    product_id = serializers.IntegerField(required=False, write_only=True, help_text="Used for single item orders")
    quantity = serializers.IntegerField(required=False, write_only=True, min_value=1, max_value=25, help_text="Used for single item orders")

    # --- FOR THE RAW DATA (Multiple Items Support) ---
    items = OrderItemSerializer(many=True, required=False)

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("This product is currently unavailable.")
        return value

    # 2. Logic-level validation: Can we check stock early?
    def validate(self, data):
        product = Product.objects.get(id=data['product_id'])
        if product.stock_quantity < data['quantity']:
            raise serializers.ValidationError({
                "quantity": f"Only {product.stock_quantity} items left in stock."
            })
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