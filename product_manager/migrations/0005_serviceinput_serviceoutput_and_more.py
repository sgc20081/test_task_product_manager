# Generated by Django 4.2.7 on 2023-11-24 10:48

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product_manager', '0004_product_balance'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceInput',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nomenclature', models.CharField(max_length=300)),
                ('quantity', models.DecimalField(decimal_places=3, max_digits=15)),
                ('price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('tax_rate', models.DecimalField(decimal_places=0, max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('bill', models.IntegerField()),
                ('sub_account', models.CharField(max_length=300)),
                ('document_service_input', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_input', to='product_manager.documentproductinput')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceOutput',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nomenclature', models.CharField(max_length=300)),
                ('quantity', models.DecimalField(decimal_places=3, max_digits=15)),
                ('price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('tax_rate', models.DecimalField(decimal_places=0, max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('bill', models.IntegerField()),
                ('sub_account', models.CharField(max_length=300)),
            ],
        ),
        migrations.AddField(
            model_name='documentproductoutput',
            name='contract',
            field=models.CharField(max_length=300, null=True),
        ),
        migrations.DeleteModel(
            name='Service',
        ),
        migrations.AddField(
            model_name='serviceoutput',
            name='document_service_output',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_output', to='product_manager.documentproductoutput'),
        ),
    ]
