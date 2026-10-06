from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from bot import database as db
from bot.config import CURRENCY


# ─── Main Menu Keyboard ──────────────────────────────────

def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Kategoriyalar"), KeyboardButton(text="🛒 Savatim")],
            [KeyboardButton(text="📋 Buyurtmalarim"), KeyboardButton(text="ℹ️ Ma'lumot")],
        ],
        resize_keyboard=True,
    )


# ─── Categories Keyboard ─────────────────────────────────

def categories_kb() -> InlineKeyboardMarkup:
    cats = db.get_categories()
    buttons = []
    for cat_id, cat_data in cats.items():
        buttons.append([InlineKeyboardButton(
            text=cat_data["name"],
            callback_data=f"cat:{cat_id}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ─── Products in Category Keyboard ───────────────────────

def products_kb(category_id: str) -> InlineKeyboardMarkup:
    products = db.get_products()
    cat_products = {k: v for k, v in products.items() if v.get("category") == category_id}
    buttons = []
    for pid, p in cat_products.items():
        buttons.append([InlineKeyboardButton(
            text=f"{p['name']} — {p['price']:,} {CURRENCY}",
            callback_data=f"prod:{pid}"
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_cats")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ─── Product Detail Keyboard ─────────────────────────────

def product_detail_kb(product_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Savatga qo'shish", callback_data=f"add_cart:{product_id}")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_products")],
    ])


# ─── Cart Keyboard ───────────────────────────────────────

def cart_kb(user_id: int) -> InlineKeyboardMarkup:
    cart = db.get_cart(user_id)
    buttons = []
    for pid, qty in cart.items():
        product = db.get_product(pid)
        if product:
            buttons.append([
                InlineKeyboardButton(text=f"➖", callback_data=f"cart_minus:{pid}"),
                InlineKeyboardButton(text=f"{product['name']} x{qty}", callback_data=f"cart_info:{pid}"),
                InlineKeyboardButton(text=f"➕", callback_data=f"cart_plus:{pid}"),
            ])
            buttons.append([
                InlineKeyboardButton(text=f"❌ {product['name']} ni o'chirish", callback_data=f"cart_remove:{pid}")
            ])
    if cart:
        buttons.append([InlineKeyboardButton(text="✅ Buyurtma berish", callback_data="create_order")])
        buttons.append([InlineKeyboardButton(text="🗑️ Savatni tozalash", callback_data="clear_cart")])
    else:
        buttons.append([InlineKeyboardButton(text="📦 Xaridni boshlash", callback_data="back_to_cats")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ─── Order Keyboard ──────────────────────────────────────

def order_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order")],
    ])


# ─── User Orders Keyboard ────────────────────────────────

def user_orders_kb(user_id: int) -> InlineKeyboardMarkup:
    orders = db.get_user_orders(user_id)
    buttons = []
    for oid, o in reversed(list(orders.items())):
        status_emoji = {"pending": "⏳", "confirmed": "✅", "shipped": "🚚", "delivered": "📦", "cancelled": "❌"}.get(o.get("status", ""), "❓")
        buttons.append([InlineKeyboardButton(
            text=f"{status_emoji} Buyurtma #{oid[-6:]} — {o.get('total', 0):,} {CURRENCY}",
            callback_data=f"order:{oid}"
        )])
    if not buttons:
        buttons.append([InlineKeyboardButton(text="📦 Xaridni boshlash", callback_data="back_to_cats")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ─── Admin Panel Keyboard ────────────────────────────────

def admin_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Mahsulotlar", callback_data="admin_products")],
        [InlineKeyboardButton(text="📂 Kategoriyalar", callback_data="admin_categories")],
        [InlineKeyboardButton(text="📋 Buyurtmalar", callback_data="admin_orders")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
    ])


def admin_products_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yangi mahsulot", callback_data="admin_add_product")],
        [InlineKeyboardButton(text="📋 Mahsulotlar ro'yxati", callback_data="admin_list_products")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back")],
    ])


def admin_product_list_kb() -> InlineKeyboardMarkup:
    products = db.get_products()
    buttons = []
    for pid, p in products.items():
        buttons.append([InlineKeyboardButton(
            text=f"{p['name']} — {p['price']:,} {CURRENCY}",
            callback_data=f"admin_prod:{pid}"
        )])
    buttons.append([InlineKeyboardButton(text="➕ Yangi mahsulot", callback_data="admin_add_product")])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_products")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_product_detail_kb(product_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"admin_edit_prod:{product_id}")],
        [InlineKeyboardButton(text="🗑️ O'chirish", callback_data=f"admin_del_prod:{product_id}")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_list_products")],
    ])


def admin_categories_kb() -> InlineKeyboardMarkup:
    cats = db.get_categories()
    buttons = []
    for cat_id, cat_data in cats.items():
        buttons.append([
            InlineKeyboardButton(text=cat_data["name"], callback_data=f"admin_cat:{cat_id}"),
            InlineKeyboardButton(text="🗑️", callback_data=f"admin_del_cat:{cat_id}"),
        ])
    buttons.append([InlineKeyboardButton(text="➕ Yangi kategoriya", callback_data="admin_add_category")])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_orders_kb() -> InlineKeyboardMarkup:
    orders = db.get_orders()
    buttons = []
    for oid, o in reversed(list(orders.items())):
        status_emoji = {"pending": "⏳", "confirmed": "✅", "shipped": "🚚", "delivered": "📦", "cancelled": "❌"}.get(o.get("status", ""), "❓")
        buttons.append([InlineKeyboardButton(
            text=f"{status_emoji} #{oid[-6:]} — {o.get('total', 0):,} {CURRENCY}",
            callback_data=f"admin_order:{oid}"
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_order_detail_kb(order_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏳ Kutilmoqda", callback_data=f"admin_set_status:{order_id}:pending")],
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"admin_set_status:{order_id}:confirmed")],
        [InlineKeyboardButton(text="🚚 Yetkazilmoqda", callback_data=f"admin_set_status:{order_id}:shipped")],
        [InlineKeyboardButton(text="📦 Yetkazildi", callback_data=f"admin_set_status:{order_id}:delivered")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"admin_set_status:{order_id}:cancelled")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_orders")],
    ])
