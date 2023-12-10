from django.urls import path
from .views import index, edit_item, search, generate_pdf
urlpatterns = [
    path('', index, name='index'),
    path('edit_item/<int:item_id>/', edit_item, name='edit_item'),
    path('search/', search, name='search'),
    path('generate_pdf/', generate_pdf, name='generate_pdf'),
]