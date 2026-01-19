from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from products.models import Product

class ProductInfrastructureTest(APITestCase):
    def setUp(self):
        Product.objects.create(name="Cache Test", sku="CH-01", price=10, is_active=True)

    def test_middleware_request_id(self):
        """PRD Section 6: Verify Middleware attaches unique request ID."""
        response = self.client.get(reverse('product-list'))
        self.assertIn('X-Request-ID', response.headers)
        # Verify it's a valid UUID string length
        self.assertEqual(len(response.headers['X-Request-ID']), 36)

    def test_product_list_unauthenticated(self):
        """PRD Section 10: Product list should be public."""
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_search_filtering(self):
        """PRD Section 10: Test search functionality."""
        url = f"{reverse('product-list')}?search=Cache"
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 1)