import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.postgres.search import SearchVector
from .models import Category, Product, OrderItem
from .forms import SearchForm, CartAddProductForm, OrderForm, OrderItemForm
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Count, Sum
from .cart import Cart
from shop.models import Product, Customer, Order


# Create your views here.

def product_list(request, category_slug=None):
    try:
        category = None
        categories = Category.objects.all()
        products = Product.objects.filter(available=True)

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)

        return render(
            request, 'shop/product/list.html',
            {
            'category': category,
            'categories': categories,
            'products': products
            })
    except Exception as e:
        return HttpResponse("Error: {}".format(str(e)), status=500)


def product_detail(request, id, slug):
    try:
        product = get_object_or_404(Product,
        id=id,
        slug=slug,
        available=True
        )
        cart_product_form = CartAddProductForm()
        return render(
            request, 'shop/product/detail.html',
            {'product': product,
            'cart_product_form': cart_product_form
            })
    except Exception as e:
        return HttpResponse("Error: {}".format(str(e)), status=500)
    

def product_search(request):
    try:
        form = SearchForm()
        query = None
        results = []
        if 'query' in request.GET:
            form = SearchForm(request.GET)
            if form.is_valid():
                query = form.cleaned_data['query']
                results = Product.objects.annotate(
                    search=SearchVector('name'),
                    ).filter(search=query)
        return render(request,
                        'shop/product/search.html',
                        {'form': form,
                        'query': query,
                        'results': results})
    except Exception as e:
        return HttpResponse("Error: {}".format(str(e)), status=500)
    

@login_required
def dashboard(request):
    try:
        # Get the most common items sold
        most_common_items = OrderItem.objects.values('product__name').annotate(total_sold=Count('product')).order_by('-total_sold')[:10]

        # Get the distribution of customers by country
        customer_distribution = Customer.objects.values('order').annotate(total_customers=Count('user_id'))

        # Get the order count and total amount by date
        order_data = Order.objects.values('created').annotate(order_count=Count('id'), total_amount=Sum('items'))

        # Convert the data to lists for plotting
        most_common_items_names = [item['product__name'] for item in most_common_items]
        most_common_items_counts = [item['total_sold'] for item in most_common_items]

        customer_countries = [customer['order'] for customer in customer_distribution]
        customer_counts = [customer['total_customers'] for customer in customer_distribution]

        order_dates = [order['created'] for order in order_data]
        order_counts = [order['order_count'] for order in order_data]
        order_amounts = [order['total_amount'] for order in order_data]

        # Create bar plot for most common items sold
        plt.figure(figsize=(10, 6))
        sns.barplot(x=most_common_items_names, y=most_common_items_counts)
        plt.title('Most Common Items Sold')
        plt.xlabel('Product')
        plt.ylabel('Total Sold')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save plot to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_data = buffer.getvalue()
        buffer.close()

        # Encode plot data to base64 for embedding in HTML
        plot_base64 = base64.b64encode(plot_data).decode('utf-8')

        context = {
            'most_common_items_names': most_common_items_names,
            'most_common_items_counts': most_common_items_counts,
            # 'customer_countries': customer_countries,
            'customer_counts': customer_counts,
            'order_dates': order_dates,
            'order_counts': order_counts,
            'order_amounts': order_amounts,
            'plot_base64': plot_base64
        }

        return render(request, 'shop/product/dashboard.html', context)

    except Exception as e:
        return HttpResponse("Error: {}".format(str(e)), status=500)
    

@require_POST
def cart_add(request, product_id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        form = CartAddProductForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(
                product=product, 
                quantity=cd['quantity'], 
                update_quantity=cd['update'])
        return redirect('cart_detail')
    except Exception as e:
        return HttpResponse("Error: {}".format(str(e)), status=500)
    

def cart_remove(request, product_id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return redirect('cart_detail')
    except Exception as e:
        return HttpResponse("Error: {}".format(str(e)), status=500)
    

def cart_detail(request):
    try:
        cart = Cart(request)
        for item in cart:
            item['update_quantity_form'] = CartAddProductForm(
                initial={'quantity': item['quantity'], 
                        'update': True})
        return render(request, 'cart/detail.html', {'cart': cart})
    except Exception as e:
        return HttpResponse("Error: {}".format(str(e)), status=500)
    

# def order_create(request):
#     try:
#         cart = Cart(request)
#         if request.method == 'POST':
#             form = OrderCreateForm(request.POST)
#             if form.is_valid():
#                 order = form.save()
#                 for item in cart:
#                     OrderItem.objects.create(order=order,
#                     product=item['product'],
#                     price=item['price'],
#                     quantity=item['quantity'])
#                 # clear the cart
#                 cart.clear()
#             return render(request,
#                         'orders/order/created.html',
#                         {'order': order})
#         else:
#             form = OrderCreateForm()
#         return render(request, 
#                     'orders/order/create.html', 
#                     {'cart': cart, 'form': form})
#     except Exception as e:
#         return HttpResponse("Error: {}".format(str(e)), status=500)


def order_create(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        order_item_form = OrderItemForm(request.POST)
        if order_form.is_valid() and order_item_form.is_valid():
            order = order_form.save(commit=False)
            order.customer = request.user.customer  # set the customer as the current user's customer
            order.save()
            order_item = order_item_form.save(commit=False)
            order_item.order = order
            order_item.save()
            # process other order items as needed
            return render(request,
                        'orders/order/created.html',
                        {'order': order})
    else:
        order_form = OrderForm(initial={'customer': request.user.customer})  # set the initial value for customer field
        order_item_form = OrderItemForm()
    context = {
        'order_form': order_form,
        'order_item_form': order_item_form
    }
    return render(request, 
                    'orders/order/create.html', 
                    context)
