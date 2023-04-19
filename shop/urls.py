from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('login/', 
        auth_views.LoginView.as_view(
        template_name='registration/login.html'), name='login'),
    path('logout/', 
        auth_views.LogoutView.as_view(
        template_name='registration/log_out.html'), name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('cart_detail', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    path('create/', views.order_create, name='order_create'),
    
    path('', views.product_list, name='product_list'),
    path('search/', views.product_search, name='product_search'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    
]
