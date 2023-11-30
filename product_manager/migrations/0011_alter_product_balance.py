# Generated by Django 4.2.7 on 2023-11-27 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_manager', '0010_product_product_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='balance',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=15, null=True),
        ),
    ]
