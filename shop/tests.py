from django.test import TestCase
from django.urls import reverse
from .models import Category, Product


# Create your tests here.

class ProductTests(TestCase):
    def setUp(self):
        # Create a test category
        self.category = Category.objects.create(name='Test Category', slug='test-category')

    def test_product_creation(self):
        # Create a test product with a valid price
        product = Product.objects.create(
            category=self.category,
            name='Test Product',
            slug='test-product',
            price=10.99,  # Set a valid price here
            available=True
        )

        # Assert that the product was created successfully
        self.assertEqual(product.name, 'Test Product')
        # Add more assertions as needed