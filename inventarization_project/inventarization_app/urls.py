from django.urls import path
from .views import index, edit_item, search, scan_qr

urlpatterns = [
    path('', index, name='index'),
    path('edit_item/<int:item_id>/', edit_item, name='edit_item'),
    path('search/', search, name='search'),
    path('scan_qr/', scan_qr, name='scan_qr'),
]