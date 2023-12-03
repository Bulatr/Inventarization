from django.shortcuts import render
from .utils import update_google_sheets, generate_qr_code
from django.shortcuts import render, get_object_or_404, redirect
from .models import InventoryItem
from .forms import InventoryItemForm
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials


def index(request):
    # Подключение к Google Sheets
    # Получить абсолютный путь к текущему файлу (где находится views.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Укажите путь к файлу ключа JSON, полученному при создании сервисного аккаунта в Google Cloud Console
    json_keyfile = os.path.join(current_dir, 'google', 'inventarization-406909-2d4115d42a80.json')

    # Укажите имя вашего файла Google Spreadsheet
    spreadsheet_name = '1954jT48OlyuveDW4qW21796c_1AurAvlN-eYVKm6Zys'

    # Укажите имена листов и заголовки столбцов
    sheet_name = 'Наш список 2023'
    columns = ['Номер','Инвентарный номер', 'Новый номер', 'Совпадение с бухгалтерией', 'Местоположение', 'Тип оборудования', 'Модель если не совпадает со списком']

    # Авторизация в Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    gc = gspread.authorize(credentials)

    # Открываем таблицу
    worksheet = gc.open_by_key(spreadsheet_name).worksheet(sheet_name)

    # Получаем все значения из листа
    all_rows = worksheet.get_all_values()

    # Первая строка содержит заголовки колонок
    headers = all_rows[0]

    # Остальные строки содержат данные
    data = all_rows[1:]

    # Передача данных в контекст шаблона
    context = {'headers': headers, 'data': data, 'rows_with_index': enumerate(all_rows)}

    return render(request, 'inventarization_app/index.html', context)

def edit_item(request, item_id):
    # Подключение к Google Sheets
    # Получить абсолютный путь к текущему файлу (где находится views.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Укажите путь к файлу ключа JSON, полученному при создании сервисного аккаунта в Google Cloud Console
    json_keyfile = os.path.join(current_dir, 'google', 'inventarization-406909-2d4115d42a80.json')

    # Укажите имя вашего файла Google Spreadsheet
    spreadsheet_name = '1954jT48OlyuveDW4qW21796c_1AurAvlN-eYVKm6Zys'

    # Укажите имена листов и заголовки столбцов
    sheet_name = 'Наш список 2023'
    columns = ['Номер','Инвентарный номер', 'Новый номер', 'Совпадение с бухгалтерией', 'Местоположение', 'Тип оборудования', 'Модель если не совпадает со списком']

    # Авторизация в Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    gc = gspread.authorize(credentials)
    try:
        # Открываем таблицу по имени
        # Открываем таблицу
        worksheet = gc.open_by_key(spreadsheet_name).worksheet(sheet_name)
        # Получаем данные по индексу строки
        row_data = worksheet.row_values(int(item_id))
        # Проверяем, что строка существует
        if not row_data:
            raise Http404("Строка не найдена")

        # Заполняем форму данными из строки
        form = InventoryItemForm(initial={
            'inventory_number': row_data[1],
            'new_number': row_data[2],
            # Добавьте другие поля по необходимости
        })

        if request.method == 'POST':
            # Если форма отправлена, обрабатываем данные
            form = InventoryItemForm(request.POST)

            if form.is_valid():
                # Обновляем данные в таблице
                updated_data = [
                    form.cleaned_data['inventory_number'],
                    form.cleaned_data['new_number'],
                    # Обновите другие поля по необходимости
                ]

                worksheet.update_row(int(item_id), updated_data)

                # Перенаправляем на страницу с подробностями после успешного обновления
                return redirect('item_details', item_id=item_id)

        return render(request, 'inventarization_app/edit_item.html', {'form': form, 'item_id': item_id})

    except gspread.exceptions.APIError as e:
        # Обработка ошибок, связанных с API Google Sheets
        print(f"Ошибка API: {e}")
        raise Http404("Ошибка API Google Sheets")



def search(request):
    if request.method == 'GET':
        query = request.GET.get('q')
        items = InventoryItem.objects.filter(inventory_number__icontains=query)
        return render(request, 'inventarization_app/index.html', {'items': items})

def scan_qr(request):
    qr_code_data = request.GET.get('qr_code', '')
    
    if qr_code_data:
        # Создаем временный объект InventoryItem для передачи данных в форму
        temp_item = InventoryItem(qr_code=generate_qr_code(qr_code_data))
        form = InventoryItemForm(instance=temp_item)
    else:
        form = InventoryItemForm()

    return render(request, 'inventarization_app/scan_qr.html', {'form': form})
