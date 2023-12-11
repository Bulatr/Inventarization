from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from django.shortcuts import render
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
import qrcode
from PIL import Image
from django.http import Http404
from django.http import HttpResponse
from .models import InventoryItem
from .forms import InventoryItemForm
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
from reportlab.lib.pagesizes import A4

def generate_qr_code(data, size):
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,  # Здесь задается размер блока в пикселях
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Изменение размера изображения с учетом размера бумаги
    img = img.resize((size, size))

    return img

def generate_pdf(request):
    # Получите все инвентарные номера из вашей модели
    # Подключение к Google Sheets
    spreadsheet_name = '1954jT48OlyuveDW4qW21796c_1AurAvlN-eYVKm6Zys'
    sheet_name = 'Наш список 2023'
    # Открываем таблицу
    worksheet = get_worksheet(spreadsheet_name, sheet_name)

    all_rows = get_all_items(worksheet)
    inventory_items = all_rows

    # Создайте временный файл для сохранения PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="qrcodes.pdf"'

    # Создайте PDF-документ с использованием reportlab
    # Поменяли ориентацию на горизонтальную
    p = canvas.Canvas(response, pagesize=landscape(A4))
    

    # Определите начальные координаты для вывода QR-кодов
    x, y = 30, 30

    for index, item in enumerate(inventory_items, start=1):
        if index >= 2:
            inventory_number = item[1]
            if inventory_number != "":
                location = item[6]
                # Создайте QR-код для инвентарного номера
                qr_code = generate_qr_code(inventory_number, size=120)  # Уменьшили размер QR-кода
                # проверяем на существование папки
                qr_codes_dir = os.path.join("media", "qrcodes")
                os.makedirs(qr_codes_dir, exist_ok=True)
                # Рисуем QR-код на PDF-документе
                img_path = os.path.join("media", f"qrcodes/{inventory_number}.png")
                qr_code.save(img_path)
                # Устанавливаем шрифт
                p.setFont("Helvetica", 14)
                p.drawInlineImage(img_path, x - 8, y - A4[0], width=70, height=70)  # Изменены размеры QR-кода и координаты
                # Выводим инвентарный номер и местоположение
                p.drawCentredString(x+30, y - 70, inventory_number)
                p.drawCentredString(x, y - 15, location)

                # Увеличиваем координаты для следующего блока
                x += 100  # Изменены координаты по X

                # Переходим на следующую строку после 4 блоков
                if index % 4 == 0:
                    x = 30
                    y += 120  # Изменены координаты по Y

                # Если достигнут конец страницы, добавляем новую страницу
                if y >= A4[1] - 25:
                    p.showPage()
                    x, y = 30, 30

    p.save()

    return response

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


