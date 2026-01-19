#type: ignore
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import AllowAny

# App Imports
from .models import Product
from .serializers import ProductListSerializer


class ProductListAPIView(generics.ListAPIView):
    """
    PRD Section 10: REST API for Product Listing with Pagination.
    PRD Section 13: High-performance Redis Caching.

    This view allows users to browse the catalog, search for specific
    items, and filter by price without hitting the database repeatedly.
    """
    # 1. Data Source: Optimized query (only active products, newest first)
    queryset = Product.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = ProductListSerializer
    # 2. Permissions: Public access for the product catalog
    permission_classes = [AllowAny]

    # 3. Filtering, Searching, and Ordering (PRD Section 10)
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['price']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'created_at']

    # 4. Caching Logic (PRD Section 13)
    # Caches the entire JSON response in Redis (DB 1) for 15 minutes.
    # Note: Ensure you visit the page in an Incognito window to trigger
    # the cache without Session/Cookie interference.
    @method_decorator(cache_page(60 * 15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ProductDetailAPIView(generics.RetrieveAPIView):
    """
    PRD Section 10: Fetch a single product's details.
    Used when a user clicks on a specific product from the list.
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'  # Access via /api/products/<id>/