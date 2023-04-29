import random
import decimal
import csv
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from django.db import models
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from django.utils.text import slugify

from shop.models import Cart, Customer, OrderItem, Order, Product, Category

class Command(BaseCommand):
    help = 'Load data into the tables'

    def handle(self, *args, **options):

        fake = Faker()

        # drop the tables - use this order due to foreign keys - so that we can rerun the file as needed without repeating values
        Cart.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Category.objects.all().delete()
        Product.objects.all().delete()
        Customer.objects.all().delete()
        User.objects.all().delete()
        print("tables dropped successfully")

        # create some customers
        # we convert some values from tuples to strings
        for i in range(10):
            first_name = fake.first_name(),
            first_name = str(first_name[0])
            last_name = fake.last_name(),
            last_name = str(last_name[0])
            username = first_name + last_name,
            username = username[0]
            user = User.objects.create_user(
                username = username,
                first_name = first_name,
                last_name = last_name,
                email = fake.ascii_free_email(), 
                password = 'Password@1'
                )
            customer = Customer.objects.get(user = user)
            customer.address = fake.address(),
            customer.address = str(customer.address[0])
            customer.save()

        # create some categories
        categories = []
        for i in range(5):
            category_name = fake.word()
            category_slug = slugify(category_name)  # generate slug from category name
            if Category.objects.filter(slug=category_slug).exists():  # check if slug already exists, regenerate if needed
                category_slug = slugify(category_name)
            category = Category.objects.create(
                name=category_name,
                slug=category_slug  # set the generated slug for the category
            )
            categories.append(category)

        # # create some products
        # products = []
        # for i in range(5):
        #     product_name = fake.catch_phrase()
        #     image_data = fake.binary(length=1024)  # Generate fake image data
        #     image_file = ContentFile(image_data)    # Create a ContentFile from the image data
        #     image_name = fake.file_name(extension='jpg')
        #     uploaded_file = SimpleUploadedFile(
        #         name=image_name, 
        #         content=image_file.read(),
        #         content_type='image/jpeg'
        #     )
        #     product_slug = slugify(product_name)  # generate slug from category name
        #     if Product.objects.filter(slug=product_slug).exists():  # check if slug already exists, regenerate if needed
        #         product_slug = slugify(product_name)
        #     product = Product.objects.create(
        #         name=product_name,
        #         slug=product_slug,  # set the generated slug for the category
        #         price=int(decimal.Decimal(random.randrange(155, 899)) / 100),
        #         category=random.choice(categories), # attach a random category to the product
        #         image=uploaded_file
        #     )
        #     products.append(product)

        # Read data from CSV file
        csv_file_path = 'data/exoplanets.csv'  # Update this with the path to your CSV file
        with open(csv_file_path, newline='', encoding="utf8") as file:
            reader = csv.reader(file, delimiter=",")
            next(reader)
            for row in reader:
                # Extract data from CSV row
                product_name = row[0]
                product_slug = slugify(product_name)
                if Product.objects.filter(slug=product_slug).exists():
                    product_slug = slugify(product_name)

                # Create Product instance
                products = Product.objects.create(
                    name=product_name,
                    slug=product_slug,
                    price=int(decimal.Decimal(random.randrange(155, 899)) / 100),
                    category=random.choice(categories)
                )

        # create some carts
        products = list(Product.objects.all())
        for i in range(10):
            random_id = random.randint(0, len(products) - 1)  # update range to be 0 to len(products) - 1
            cart = Cart.objects.create(
                product=products[random_id],
                quantity=random.randrange(1, 4),
            )
            cart.save()

        # create some orders
        customers = list(Customer.objects.all())
        for customer in customers:
            order = Order.objects.create(
                customer=customer,
            )
            order_items = Cart.objects.filter()  # update filter to use 'created_date' and 'cart_owner' fields
            for cart_item in order_items:
                order_item = OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price * cart_item.quantity  # set price to be product price multiplied by quantity
                )
                order_item.save()
            order.save()


        # example of creating an OrderItem instance
        # NOTE: This example is not used in the main part of the code and may need to be revised to properly use it
        # create an OrderItem instance with a previously created Order and Product instance
        example_order = Order.objects.first()
        example_product = Product.objects.first()
        example_order_item = OrderItem(
            order=example_order,
            product=example_product,
            quantity=random.randrange(1, 4),
            price=example_product.price * random.randrange(1, 4)
        )
        example_order_item.save()
        
        print("Data loaded successfully")
