import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Admin ID larini olish
raw_admins = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = []
for admin_id in raw_admins.split(","):
    admin_id = admin_id.strip()
    if admin_id.isdigit():
        ADMIN_IDS.append(int(admin_id))

DB_PATH = os.getenv("DB_PATH", "shop.db")
if not os.path.isabs(DB_PATH):
    DB_PATH = str(BASE_DIR / DB_PATH)


def is_admin(user_id: int) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish"""
    return user_id in ADMIN_IDS
