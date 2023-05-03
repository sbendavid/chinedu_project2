from django import forms
from .models import Order, OrderItem


PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]

class SearchForm(forms.Form):
    query = forms.CharField()

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES, 
        coerce=int)
    update = forms.BooleanField(
        required=False, 
        initial=False, 
        widget=forms.HiddenInput)


# class OrderCreateForm(forms.ModelForm):
#     class Meta:
#         model = Order
#         fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']  # specify other fields you want to include in the order form
        widgets = {
            'customer': forms.HiddenInput()  # set the customer field as a hidden input field
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']  # specify fields you want to include in the order item form
