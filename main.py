import os
import shopify
from gspread import service_account
from twilio.rest import Client
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from dotenv import load_dotenv

load_dotenv()

# Shopify API Setup
API_KEY = os.getenv('SHOPIFY_API_KEY')
PASSWORD = os.getenv('SHOPIFY_PASSWORD')
STORE_URL = os.getenv('SHOPIFY_STORE_URL')

# Google Sheets Setup
GC = service_account(filename='credentials.json')
SHEET = GC.open("Shopify Orders").sheet1

# Twilio Setup
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')
CUSTOMER_NUMBER = os.getenv('CUSTOMER_NUMBER')

def fetch_shopify_orders():
    shopify.ShopifyResource.set_site(f"https://{API_KEY}:{PASSWORD}@{STORE_URL}.myshopify.com/admin/api/2023-01")
    orders = shopify.Order.find(status="open")
    return orders

def log_to_google_sheets(order):
    SHEET.append_row([
        order.id,
        order.created_at,
        order.total_price,
        order.customer.email
    ])

def send_sms_notification(order):
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    client.messages.create(
        body=f"New Order #{order.id} - ${order.total_price}",
        from_=TWILIO_NUMBER,
        to=CUSTOMER_NUMBER
    )

def generate_invoice(order):
    filename = f"invoice_{order.id}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, f"Invoice #: {order.id}")
    c.drawString(100, 730, f"Date: {order.created_at}")
    c.drawString(100, 710, f"Total: ${order.total_price}")
    c.save()
    return filename

if __name__ == "__main__":
    orders = fetch_shopify_orders()
    for order in orders:
        log_to_google_sheets(order)
        send_sms_notification(order)
        generate_invoice(order)
