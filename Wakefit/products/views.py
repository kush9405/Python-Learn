from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

# App Imports
from .models import Product
from .serializers import ProductSerializer


class ProductListAPIView(generics.ListAPIView):
    """
    PRD Section 10: REST API for Product Listing.
    PRD Section 13: Implements Redis Caching.
    """
    # 1. Data Source: Only show active products, ordered by newest first
    queryset = Product.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = ProductSerializer
    
    # 2. Permissions: Allow anyone (even logged-out users) to see the catalog
    permission_classes = [AllowAny]

    # 3. Filtering & Searching (PRD Section 10)
    # Allows users to:
    # - Filter by price: ?price=100.00
    # - Search by name/description: ?search=laptop
    # - Order by price: ?ordering=-price
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['price']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'created_at']

    # 4. Caching Logic (PRD Section 13)
    # Caches the entire JSON response in Redis for 15 minutes (900 seconds).
    # This prevents the database from being hit on every page refresh.
    @method_decorator(cache_page(60 * 15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class ProductDetailAPIView(generics.RetrieveAPIView):
    """
    Fetch a single product by its ID or SKU.
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id' # You can change this to 'sku' if preferred

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # Allow anyone to view products