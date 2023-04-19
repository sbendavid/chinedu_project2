from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.postgres.search import SearchVector
from .models import Category, Product, OrderItem
from .forms import SearchForm, OrderCreateForm, CartAddProductForm
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .cart import Cart


# Create your views here.

def product_list(request, category_slug=None):
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

def product_detail(request, id, slug):
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

def product_search(request):
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

@login_required
def dashboard(request):
    return render(
        request, 'shop/product/dashboard.html',
        {'section': 'dashboard'}
        )

@require_POST
def cart_add(request, product_id):
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

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'], 
                     'update': True})
    return render(request, 'cart/detail.html', {'cart': cart})

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity'])
            # clear the cart
            cart.clear()
        return render(request,
                    'orders/order/created.html',
                    {'order': order})
    else:
        form = OrderCreateForm()
    return render(request, 
                  'orders/order/create.html', 
                  {'cart': cart, 'form': form})
