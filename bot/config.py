import os
from dotenv import load_dotenv

# .env faylni yuklash
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# Telegram Bot Token - @BotFather dan olingan token
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Admin Telegram ID-lari (botga /start bosganingizda ID ko'rinadi)
# Bir nechta admin bo'lsa: [123456, 789012]
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "YOUR_TELEGRAM_ID").split(",") if x.strip().isdigit()]

# Ma'lumotlar bazasi fayllari
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")
CARTS_FILE = os.path.join(DATA_DIR, "carts.json")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")

# Valyuta
CURRENCY = "so'm"
