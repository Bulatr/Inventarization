from django.db import models

class InventoryItem(models.Model):
    number = models.IntegerField()
    inventory_number = models.CharField(max_length=255)
    new_number = models.CharField(max_length=255)
    previous_year_number = models.CharField(max_length=255)
    match_with_accounting = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=255)
    model_if_not_matching = models.CharField(max_length=255)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

class MainInventoryItem(models.Model):
    inventory_number_1 = models.CharField(max_length=255, verbose_name='Инвентарный номер (1)')
    inventory_number_2 = models.CharField(max_length=255, verbose_name='Инвентарный номер (2)')
    name = models.CharField(max_length=255, verbose_name='Наименование')
    location_2022 = models.CharField(max_length=255, verbose_name='Расположение в 2022 году')
    location_2023 = models.CharField(max_length=255, verbose_name='Расположение в 2023 году')
    acquisition_date = models.DateField(verbose_name='Дата принятия')
