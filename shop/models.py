from django.db import models
from django.conf import settings
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
            'product_list_by_category',
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
            'product_detail',
            args=[self.id, self.slug]
            )

class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    # braintree_id = models.CharField(max_length=150, blank=True)
    stripe_id = models.CharField(max_length=250, blank=True)
    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Order {}'.format(self.id)
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
            
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)
    
    def get_cost(self):
        return self.price * self.quantity



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
