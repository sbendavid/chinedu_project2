from django.db import models
from django.urls import reverse
from faker import Faker

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=200,
    db_index=True)
    slug = models.SlugField(max_length=200,
    unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse(
            'shop:product_list_by_category',
            args=[self.slug]
            )


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        related_name='products',
        on_delete=models.CASCADE
        )
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(
        upload_to='products/%Y/%m/%d',
        blank=True
        )
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse(
            'shop:product_detail',
            args=[self.id, self.slug]
            )


# def create_fake_data(num_categories=5, num_products=50):
#     fake = Faker()

#     # Create categories
#     for _ in range(num_categories):
#         category = Category.objects.create(
#             name=fake.word(),
#             slug=fake.slug()
#         )

#     # Create products
#     for _ in range(num_products):
#         product = Product.objects.create(
#             name=fake.word(),
#             slug=fake.slug(),
#             category=Category.objects.order_by('?').first(),
#             description=fake.sentence(),
#             price=fake.random_int(min=10, max=100),
#             available=fake.boolean()
#         )
