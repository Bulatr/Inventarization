from django import forms
from .models import InventoryItem

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['number', 'inventory_number', 'new_number', 'previous_year_number', 'match_with_accounting', 'location', 'equipment_type', 'model_if_not_matching', 'qr_code']
        widgets = {
            'qr_code': forms.HiddenInput(),
        }

class ImportForm(forms.Form):
    import_button = forms.BooleanField(initial=False, widget=forms.HiddenInput)