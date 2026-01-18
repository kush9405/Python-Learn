from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'price', 'stock_quantity']

# products/serializers.py

class ProductMinimalSerializer(serializers.ModelSerializer):
    """
    Used for nested relationships where we don't want to
    leak internal data like stock_quantity.
    """
    class Meta:
        model = Product
        # We only show ID, Name, and SKU.
        # We don't even show 'price' here because the OrderItem has the
        # specific price the user actually paid at that time.
        fields = ['id', 'name', 'sku']