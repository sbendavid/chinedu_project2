from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from shop.models import Category, Product
from shop.forms import CartAddProductForm, SearchForm
from django.contrib.postgres.search import SearchVector


def product_list(request, category_slug=None):
    try:
        category = None
        categories = Category.objects.all()
        products = Product.objects.filter(available=True)

        if category_slug:
            category = get_object_or_404(
                Category, 
                slug=category_slug)
            products = products.filter(category=category)

        return render(request,
            'shop/product/list.html',
            {'category': category,
            'categories': categories,
            'products': products})
    except Exception as e:
        return HttpResponse("Error: {}".format(str(e)), status=500)

def product_detail(request, id, slug):
    try:
        product = get_object_or_404(
            Product,
            id=id,
            slug=slug,
            available=True)
        cart_product_form = CartAddProductForm()

        return render(request,
            'shop/product/detail.html',
            {'product': product,
            'cart_product_form': cart_product_form})
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