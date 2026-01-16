from linecache import cache
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=50, unique=True) # Stock Keeping Unit (Master Data Unique ID)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # When a product is saved, clear the cache so users see fresh data
        cache.clear() 
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name} ({self.sku})"