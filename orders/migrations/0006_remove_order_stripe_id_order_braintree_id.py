# Generated by Django 4.2 on 2023-04-12 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_remove_order_braintree_id_order_stripe_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='stripe_id',
        ),
        migrations.AddField(
            model_name='order',
            name='braintree_id',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]