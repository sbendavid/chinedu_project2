from django.urls import path
from django.contrib.auth import views as auth_views
from shop.views import main, cart, customer, orders, product


urlpatterns = [
    path('customers/', customer.customer_list, name='customer_list'),
    path('customers/<int:id>/', customer.customer_detail, name='customer_detail'),

    path('order_list/', orders.order_list, name='order_list'),
    path('order/<int:id>/', orders.order_detail, name= 'order_detail'),
    
    path('login/', 
        auth_views.LoginView.as_view(
        template_name='registration/login.html'), name='login'),
    path('logout/', 
        auth_views.LogoutView.as_view(
        template_name='registration/log_out.html'), name='logout'),

    path('dashboard/', main.dashboard, name='dashboard'),
    
    path('cart_detail', cart.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', cart.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', cart.cart_remove, name='cart_remove'),

    path('create/', orders.order_create, name='order_create'),
    
    path('', product.product_list, name='product_list'),
    path('search/', product.product_search, name='product_search'),
    path('<slug:category_slug>/', product.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', product.product_detail, name='product_detail'),
    
]
