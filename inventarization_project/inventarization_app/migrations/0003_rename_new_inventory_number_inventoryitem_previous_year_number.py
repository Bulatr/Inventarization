# Generated by Django 4.2.7 on 2023-12-04 13:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventarization_app', '0002_inventoryitem_new_inventory_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inventoryitem',
            old_name='new_inventory_number',
            new_name='previous_year_number',
        ),
    ]