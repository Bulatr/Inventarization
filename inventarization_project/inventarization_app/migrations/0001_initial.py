# Generated by Django 4.2.7 on 2023-12-03 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('inventory_number', models.CharField(max_length=255)),
                ('new_number', models.CharField(max_length=255)),
                ('match_with_accounting', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('equipment_type', models.CharField(max_length=255)),
                ('model_if_not_matching', models.CharField(max_length=255)),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='qr_codes/')),
            ],
        ),
    ]
