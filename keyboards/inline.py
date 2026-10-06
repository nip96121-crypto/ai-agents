from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any
from utils.helpers import format_currency


def categories_keyboard(categories: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Kategoriyalar ro'yxati inline tugmalari"""
    buttons = []
    # Har bir qatorda 2 tadan kategoriya
    row = []
    for cat in categories:
        row.append(InlineKeyboardButton(text=cat["name"], callback_data=f"cat_{cat['id']}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton(text="🛒 Savatchaga o'tish", callback_data="view_cart")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def products_keyboard(category_id: int, products: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Kategoriya ichidagi mahsulotlar inline tugmalari"""
    buttons = []
    for p in products:
        text = f"{p['name']} | {format_currency(p['price'])}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"prod_{p['id']}")])

    buttons.append([
        InlineKeyboardButton(text="⬅️ Kategoriyalar", callback_data="catalog"),
        InlineKeyboardButton(text="🛒 Savatcha", callback_data="view_cart")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def product_detail_keyboard(product_id: int, category_id: int, quantity: int = 1) -> InlineKeyboardMarkup:
    """Mahsulot tafsilotlari va savatchaga qo'shish klaviaturasi"""
    qty = max(1, quantity)
    buttons = [
        [
            InlineKeyboardButton(text="➖", callback_data=f"qty_dec_{product_id}_{qty}"),
            InlineKeyboardButton(text=f"🔢 {qty} dona", callback_data="noop"),
            InlineKeyboardButton(text="➕", callback_data=f"qty_inc_{product_id}_{qty}")
        ],
        [
            InlineKeyboardButton(text="🛒 Savatchaga qo'shish", callback_data=f"addcart_{product_id}_{qty}")
        ],
        [
            InlineKeyboardButton(text="⬅️ Ortga", callback_data=f"cat_{category_id}"),
            InlineKeyboardButton(text="🛒 Savatcha", callback_data="view_cart")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def cart_keyboard(cart_items: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Savatcha klaviaturasi: har bir mahsulot uchun +/- va o'chirish"""
    buttons = []
    for item in cart_items:
        p_id = item["product_id"]
        qty = item["quantity"]
        name = item["name"]
        buttons.append([
            InlineKeyboardButton(text=f"📌 {name[:20]} ({qty}x)", callback_data=f"prod_{p_id}")
        ])
        buttons.append([
            InlineKeyboardButton(text="➖", callback_data=f"cart_dec_{p_id}"),
            InlineKeyboardButton(text=f"{qty} dona", callback_data="noop"),
            InlineKeyboardButton(text="➕", callback_data=f"cart_inc_{p_id}"),
            InlineKeyboardButton(text="🗑", callback_data=f"cart_del_{p_id}")
        ])

    buttons.append([InlineKeyboardButton(text="✅ Rasmiylashtirish (Buyurtma berish)", callback_data="checkout")])
    buttons.append([
        InlineKeyboardButton(text="🛍 Xaridni davom ettirish", callback_data="catalog"),
        InlineKeyboardButton(text="🧹 Savatni tozalash", callback_data="clear_cart")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def empty_cart_keyboard() -> InlineKeyboardMarkup:
    """Bo'sh savatcha uchun klaviatura"""
    buttons = [
        [InlineKeyboardButton(text="🛍 Mahsulotlarni ko'rish", callback_data="catalog")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def payment_methods_keyboard() -> InlineKeyboardMarkup:
    """To'lov usulini tanlash klaviaturasi"""
    buttons = [
        [InlineKeyboardButton(text="💵 Naqd pul (Qabul qilinganda)", callback_data="pay_cash")],
        [InlineKeyboardButton(text="💳 Plastik karta (Click / Payme orqali)", callback_data="pay_card")],
        [InlineKeyboardButton(text="❌ Buyurtmani bekor qilish", callback_data="cancel_order")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def order_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Buyurtmani tasdiqlash klaviaturasi"""
    buttons = [
        [InlineKeyboardButton(text="✅ Tasdiqlayman", callback_data="confirm_order_yes")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="confirm_order_no")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# --- ADMIN INLINE TUGMALARI ---

def admin_main_keyboard() -> InlineKeyboardMarkup:
    """Admin boshqaruv paneli menyusi"""
    buttons = [
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
            InlineKeyboardButton(text="📦 Yangi buyurtmalar", callback_data="admin_orders")
        ],
        [
            InlineKeyboardButton(text="🗂 Kategoriyalar", callback_data="admin_categories"),
            InlineKeyboardButton(text="🛍 Mahsulotlar", callback_data="admin_products")
        ],
        [
            InlineKeyboardButton(text="📢 Barcha foydalanuvchilarga xabar (Rassilka)", callback_data="admin_broadcast")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_categories_keyboard(categories: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Admin kategoriya boshqaruvi"""
    buttons = [
        [InlineKeyboardButton(text="➕ Yangi kategoriya qo'shish", callback_data="admin_add_category")]
    ]
    for cat in categories:
        buttons.append([
            InlineKeyboardButton(text=f"📁 {cat['name']}", callback_data="noop"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"admin_del_cat_{cat['id']}")
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Admin panelga qaytish", callback_data="admin_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_products_menu_keyboard(categories: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Admin mahsulot boshqaruvi uchun kategoriya tanlash"""
    buttons = [
        [InlineKeyboardButton(text="➕ Yangi mahsulot qo'shish", callback_data="admin_add_product")]
    ]
    for cat in categories:
        buttons.append([InlineKeyboardButton(text=f"📁 {cat['name']} mahsulotlari", callback_data=f"admin_cat_prods_{cat['id']}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Admin panelga qaytish", callback_data="admin_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_category_products_keyboard(category_id: int, products: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Admin ma'lum kategoriyadagi mahsulotlarni ko'rish va o'chirish"""
    buttons = []
    for p in products:
        buttons.append([
            InlineKeyboardButton(text=f"📦 {p['name'][:22]}", callback_data="noop"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"admin_del_prod_{p['id']}_{category_id}")
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Kategoriyalar ro'yxatiga", callback_data="admin_products")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_orders_list_keyboard(orders: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Admin buyurtmalar ro'yxati"""
    buttons = []
    for o in orders:
        status_icon = "⏳" if o["status"] == "pending" else ("🚚" if o["status"] == "shipping" else "✅")
        text = f"{status_icon} #{o['id']} | {format_currency(o['total_price'])} | {o['customer_name'][:15]}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"admin_order_{o['id']}")])

    buttons.append([InlineKeyboardButton(text="⬅️ Admin panelga qaytish", callback_data="admin_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_order_actions_keyboard(order_id: int, current_status: str) -> InlineKeyboardMarkup:
    """Admin buyurtma holatini o'zgartirish tugmalari"""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"status_{order_id}_confirmed"),
            InlineKeyboardButton(text="🚚 Yetkazilmoqda", callback_data=f"status_{order_id}_shipping")
        ],
        [
            InlineKeyboardButton(text="🏁 Yakunlash", callback_data=f"status_{order_id}_completed"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"status_{order_id}_cancelled")
        ],
        [
            InlineKeyboardButton(text="⬅️ Buyurtmalar ro'yxatiga", callback_data="admin_orders")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
