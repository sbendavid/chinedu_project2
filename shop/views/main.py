import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Count, Sum
from shop.models import Customer, Order, OrderItem, Category, Product
from shop.forms import CartAddProductForm, SearchForm
from django.contrib.postgres.search import SearchVector

# Create your views here.

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
    