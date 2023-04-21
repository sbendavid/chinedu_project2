from django.db.models import Count, F
from django.contrib import admin
from django.http import JsonResponse
from .models import Category, Product, Order, OrderItem
from django.urls import path
from chartjs.views import JSONView
from django.core.serializers.json import DjangoJSONEncoder
from django.template.defaultfilters import json_script
from django.db.models.functions import TruncDay
from django.db.models import Q


import json

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'slug'
        ]
    prepopulated_fields = {
        'slug': ('name',)
        }
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'slug', 
        'price',
        'available', 
        'created', 
        'updated'
        ]
    list_filter = [
        'available', 
        'created', 
        'updated'
        ]
    list_editable = [
        'price', 
        'available'
        ]
    prepopulated_fields = {
        'slug': ('name',)
        }
    
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 
                    'email','address', 'postal_code', 
                    'city', 'paid', 'created', 'updated']
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]

    def changelist_view(self, request, extra_context=None):
        # Aggregate both paid and unpaid orders per day
        chart_data = (
            Order.objects.annotate(date=TruncDay("created"))
            .annotate(paid_count=Count('id', filter=Q(paid=True)), unpaid_count=Count('id', filter=Q(paid=False)))
            .values("date", "paid_count", "unpaid_count")
            .order_by("-date")
        )

        # Serialize the chart data to JSON
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)

        # Update the extra_context with the chart_data
        extra_context = extra_context or {}
        extra_context["chart_data"] = as_json

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)
    


    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path("chart_data/", self.admin_site.admin_view(self.chart_data_endpoint))
        ]
        # NOTE! Our custom urls have to go before the default urls, because they
        # default ones match anything.
        return extra_urls + urls

    # JSON endpoint for generating chart data that is used for dynamic loading
    # via JS.
    def chart_data_endpoint(self, request):
        chart_data = self.chart_data()
        return JsonResponse(list(chart_data), safe=False)

    def chart_data(self):
        return (
            Order.objects.annotate(date=TruncDay("created"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("-date")
        )