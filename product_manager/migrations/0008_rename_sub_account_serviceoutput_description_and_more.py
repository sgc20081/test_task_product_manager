# Generated by Django 4.2.7 on 2023-11-25 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_manager', '0007_documentinput_storage_alter_documentoutput_storage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='serviceoutput',
            old_name='sub_account',
            new_name='description',
        ),
        migrations.RemoveField(
            model_name='serviceoutput',
            name='bill',
        ),
        migrations.AddField(
            model_name='serviceoutput',
            name='discount',
            field=models.DecimalField(decimal_places=2, max_digits=15, null=True),
        ),
    ]