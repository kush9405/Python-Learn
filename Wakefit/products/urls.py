from django.urls import path

from .views import ProductListAPIView

urlpatterns = [
    # This matches: /api/products/
    path('', ProductListAPIView.as_view(), name='product-list'),
]