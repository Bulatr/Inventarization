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
    columns = ['Номер','Инвентарный номер', 'Новый номер', 'Присвоенный номер в прошлом году', 'Совпадение с бухгалтерией', 'Местоположение', 'Тип оборудования', 'Модель если не совпадает со списком']

    # Авторизация в Google Sheets API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    gc = gspread.authorize(credentials)
    try:
        # Открываем таблицу по имени
        # Открываем таблицу
        worksheet = gc.open_by_key(spreadsheet_name).worksheet(sheet_name)
        # Получаем данные по индексу строки
        # Индекс строки начинается с 0, поэтому нужно добавить 1
        index_gt = int(item_id)+1
        row_data = worksheet.row_values(index_gt)
        # Проверяем, что строка существует
        if not row_data:
            raise Http404("Строка не найдена")

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
                'location': row_data[6],
                'equipment_type': row_data[7],
                'model_if_not_matching': model_if_not_matching,
                # Добавьте другие поля по необходимости
            }


        if request.method == 'POST':
            # Если форма отправлена, обрабатываем данные
            # Пример обработки данных, может потребоваться реализация по вашим потребностям
            form_data = {
                'number': request.POST.get('number'),
                'inventory_number': request.POST.get('inventory_number'),
                'new_number': request.POST.get('new_number'),
                'previous_year_number': request.POST.get('previous_year_number'),
                'match_with_accounting': request.POST.get('match_with_accounting'),
                'location': request.POST.get('location'),
                'equipment_type': request.POST.get('equipment_type'),
                'model_if_not_matching': request.POST.get('model_if_not_matching')

                # Добавьте другие поля по необходимости
            }
            # Обработайте значения других полей по необходимости

            # Теперь у вас есть значения, которые вы можете использовать
            # для обновления данных в Google таблице


            # Перенаправляем на страницу с подробностями после успешного обновления
            return redirect('item_details', item_id=item_id)

        return render(request, 'inventarization_app/edit_item.html', {'form_data': form_data, 'item_id': item_id})

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
