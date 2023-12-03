from django.db import models

class InventoryItem(models.Model):
    number = models.IntegerField()
    inventory_number = models.CharField(max_length=255)
    new_number = models.CharField(max_length=255)
    match_with_accounting = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=255)
    model_if_not_matching = models.CharField(max_length=255)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
