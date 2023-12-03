import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings
import qrcode
from PIL import Image
from io import BytesIO

def update_google_sheets(item):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(settings.GOOGLE_SHEETS_API_KEY_FILE, scope)
    client = gspread.authorize(creds)

    sheet = client.open(settings.GOOGLE_SHEETS_SPREADSHEET_NAME).worksheet(settings.GOOGLE_SHEETS_WORKSHEET_NAME)

    row = [item.number, item.inventory_number, item.new_number, item.match_with_accounting,
           item.location, item.equipment_type, item.model_if_not_matching]

    sheet.append_row(row)

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = buffer.getvalue()

    return img_str
