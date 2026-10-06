from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard(is_admin_user: bool = False) -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi"""
    keyboard = [
        [KeyboardButton(text="🛍 Mahsulotlar katalogi"), KeyboardButton(text="🛒 Savatcha")],
        [KeyboardButton(text="📦 Buyurtmalarim"), KeyboardButton(text="🔍 Mahsulot qidirish")],
        [KeyboardButton(text="ℹ️ Biz haqimizda"), KeyboardButton(text="📞 Aloqa / Yordam")]
    ]
    if is_admin_user:
        keyboard.append([KeyboardButton(text="🔐 Admin Panel")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Bo'limni tanlang..."
    )


def phone_request_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqamni yuborish klaviaturasi"""
    keyboard = [
        [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)],
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def location_request_keyboard() -> ReplyKeyboardMarkup:
    """Geolokatsiyani yuborish klaviaturasi"""
    keyboard = [
        [KeyboardButton(text="📍 Joylashuvni yuborish", request_location=True)],
        [KeyboardButton(text="✍️ Manzilni qo'lda yozish"), KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Bekor qilish klaviaturasi"""
    keyboard = [
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
