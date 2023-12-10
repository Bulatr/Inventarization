from django.shortcuts import render
from .utils import update_google_sheets, generate_qr_code
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from .models import InventoryItem
from .forms import InventoryItemForm
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials


def index(request):
    # Подключение к Google Sheets
    spreadsheet_name = '1954jT48OlyuveDW4qW21796c_1AurAvlN-eYVKm6Zys'
    sheet_name = 'Наш список 2023'
    # Открываем таблицу
    worksheet = get_worksheet(spreadsheet_name, sheet_name)

    all_rows = get_all_items(worksheet)

    # Передача данных в контекст шаблона
    context = {'rows_with_index': enumerate(all_rows)}

    return render(request, 'inventarization_app/index.html', context)

def get_all_items(worksheet):
    # Получаем все значения из листа
    all_rows = worksheet.get_all_values()

    # Первая строка содержит заголовки колонок
    headers = all_rows[0]

    # Остальные строки содержат данные
    data = all_rows[1:]

    # возвращаем все строки
    return all_rows


def edit_item(request, item_id):
    if request.method == 'POST':
        # Если форма отправлена, обрабатываем данные
        # для обновления данных в Google таблице
        # Обновляем строку в таблице
        # нужно явно указывать ячейки, ячейки с формулами не трогать
        spreadsheet_name = '1954jT48OlyuveDW4qW21796c_1AurAvlN-eYVKm6Zys'
        sheet_name = 'Наш список 2023'
        worksheet = get_worksheet(spreadsheet_name, sheet_name)
        # Получение инвентарного номера из формы
        inventory_number = request.POST.get('inventory_number')
        result_string = inventory_number.replace("0", "", 1)
        if not is_inventory_number_unique(worksheet, result_string):
            # Если номер не уникален в Google Sheets, выдать ошибку
            return render(request, 'inventarization_app/edit_item.html', {'form_data': get_sheet_item(item_id), 'item_id': item_id, 'error': 'Инвентарный номер уже существует в таблице.'})
        # если не существует записываем в таблицу
        # index_gt нумерация строк начинается с 0, поэтому добавляем 1
        index_gt = item_id+1
        worksheet.update_cell(index_gt, 1, request.POST.get('number'))
        worksheet.update_cell(index_gt, 2, request.POST.get('inventory_number'))
        worksheet.update_cell(index_gt, 4, request.POST.get('new_number'))
        worksheet.update_cell(index_gt, 7, request.POST.get('location'))
        worksheet.update_cell(index_gt, 8, request.POST.get('equipment_type'))
        worksheet.update_cell(index_gt, 9, request.POST.get('model_if_not_matching'))

        # Готовим form_data
        # Заново получим эту строку из гугл таблицы
        form_data = get_sheet_item(item_id)
        # Перенаправляем на страницу с подробностями после успешного обновления
        return render(request, 'inventarization_app/edit_item.html', {'form_data': form_data, 'item_id': item_id})
    else:
        form_data = get_sheet_item(item_id)
        return render(request, 'inventarization_app/edit_item.html', {'form_data': form_data, 'item_id': item_id})


# Подключение к таблице и получении данных
# Получение worksheet
def get_worksheet(spreadsheet_name, sheet_name):
    # Подключение к Google Sheets
    # Получить абсолютный путь к текущему файлу (где находится views.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Укажите путь к файлу ключа JSON, полученному при создании сервисного аккаунта в Google Cloud Console
    json_keyfile = os.path.join(current_dir, 'google', 'inventarization-406909-2d4115d42a80.json')

    # Укажите имя вашего файла Google Spreadsheet
    spreadsheet_name = '1954jT48OlyuveDW4qW21796c_1AurAvlN-eYVKm6Zys'

    # Укажите имена листов и заголовки столбцов
    sheet_name = 'Наш список 2023'

    # Авторизация в Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    gc = gspread.authorize(credentials)

    try:
        # Открываем таблицу по имени
        # Открываем таблицу
        worksheet = gc.open_by_key(spreadsheet_name).worksheet(sheet_name)
        return worksheet

    except gspread.exceptions.APIError as e:
        # Обработка ошибок, связанных с API Google Sheets
        print(f"Ошибка API: {e}")
        raise Http404("Ошибка API Google Sheets")

# возвращает  form_data
def get_sheet_item(item_id):
    try:
        # Открываем таблицу по имени
        spreadsheet_name = '1954jT48OlyuveDW4qW21796c_1AurAvlN-eYVKm6Zys'
        sheet_name = 'Наш список 2023'
        worksheet = get_worksheet(spreadsheet_name, sheet_name)
        # Получаем данные по индексу строки
        # Индекс строки начинается с 0, поэтому нужно добавить 1
        index_gt = int(item_id)+1
        row_data = worksheet.row_values(index_gt)

        # Проверяем, что строка существует
        if not row_data:
            raise Http404("Строка не найдена")
        # проверка на существование колонок, иногда ведет неадекватно, не может прочитать пустые значения
        if len(row_data) >=7:
            lenrow_data = len(row_data)
            location = row_data[6]
            equipment_type = row_data[7]
        else:
            location = ""
            equipment_type = ""
        # Заполняем форму данными из строки
        if len(row_data) >= 9:
            model_if_not_matching = row_data[8]
        else:
            model_if_not_matching = ""

        form_data = {
                'number': row_data[0],
                'inventory_number': row_data[1],
                'new_number': row_data[3],
                'previous_year_number': row_data[4],
                'match_with_accounting': row_data[5],
                'location': location,
                'equipment_type': equipment_type,
                'model_if_not_matching': model_if_not_matching,
                # Добавьте другие поля по необходимости
            }
        return form_data

    except gspread.exceptions.APIError as e:
        # Обработка ошибок, связанных с API Google Sheets
        print(f"Ошибка API: {e}")
        raise Http404("Ошибка API Google Sheets")

def is_inventory_number_unique(worksheet, inventory_number):
    # Получение всех значений в столбце с инвентарными номерами
    inventory_numbers_column = worksheet.col_values(2)
    # Проверка уникальности
    return inventory_number not in inventory_numbers_column

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
