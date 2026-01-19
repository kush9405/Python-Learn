# type:ignore
import random
from django.core.management.base import BaseCommand
from products.models import Product
from faker import Faker

class Command(BaseCommand):
    help = 'Seeds the database with 500 products'

    def handle(self, *args, **kwargs):
        fake = Faker()
        self.stdout.write("Seeding 500 products...")

        products_to_create = []

        # We start from current count to avoid SKU collisions if you run this twice
        current_count = Product.objects.count()

        for i in range(500):
            name = f"Wakefit {fake.word().capitalize()} {random.choice(['Mattress', 'Pillow', 'Bed', 'Chair'])}"
            sku = f"WK-{current_count + i + 1:04d}" # Generates WK-0001, WK-0002, etc.

            product = Product(
                name=name,
                description=fake.paragraph(nb_sentences=3),
                sku=sku,
                price=random.randint(500, 50000), # Realistic price range
                stock_quantity=random.randint(10, 100),
                is_active=True
            )
            products_to_create.append(product)

        # PRD Section 8 Optimization: Bulk Create is much faster than .create() in a loop
        Product.objects.bulk_create(products_to_create)

        self.stdout.write(self.style.SUCCESS(f'Successfully added 500 products! Total: {Product.objects.count()}'))