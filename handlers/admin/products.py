from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from config import is_admin
from database import db
from states.admin_states import AddProductState
from keyboards import admin_products_menu_keyboard, admin_category_products_keyboard
from utils.helpers import format_currency

router = Router()


@router.callback_query(F.data == "admin_products")
async def show_products_menu(callback: CallbackQuery, state: FSMContext):
    """Mahsulotlar boshqaruvi: toifalar ro'yxati"""
    await state.clear()
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    await callback.answer()
    cats = await db.get_categories()
    text = (
        "🛍 <b>Mahsulotlar boshqaruvi:</b>\n\n"
        "Mahsulotlarni ko'rish va o'chirish uchun toifani tanlang yoki yangi mahsulot qo'shing:"
    )
    markup = admin_products_menu_keyboard(cats)
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
    except Exception:
        await callback.message.delete()
        await callback.message.answer(text, parse_mode="HTML", reply_markup=markup)


@router.callback_query(F.data.startswith("admin_cat_prods_"))
async def show_category_products_admin(callback: CallbackQuery):
    """Tanlangan toifadagi mahsulotlar va ularni o'chirish"""
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    await callback.answer()
    category_id = int(callback.data.split("_")[3])
    cat = await db.get_category(category_id)
    cat_name = cat["name"] if cat else "Toifa"
    products = await db.get_products_by_category(category_id)

    if not products:
        text = f"📂 <b>{cat_name}</b> toifasida hali mahsulot yo'q."
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Yangi mahsulot qo'shish", callback_data="admin_add_product")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="admin_products")]
        ])
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
        return

    text = f"📂 <b>{cat_name}</b> mahsulotlari:\n\nMahsulotni o'chirish uchun 🗑 tugmasini bosing:"
    markup = admin_category_products_keyboard(category_id, products)
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)


@router.callback_query(F.data.startswith("admin_del_prod_"))
async def delete_product_admin(callback: CallbackQuery):
    """Mahsulotni o'chirish"""
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    parts = callback.data.split("_")
    prod_id = int(parts[3])
    cat_id = int(parts[4])

    prod = await db.get_product(prod_id)
    prod_name = prod["name"] if prod else "Mahsulot"

    await db.delete_product(prod_id)
    await callback.answer(f"🗑 «{prod_name}» o'chirildi!", show_alert=True)

    # Ro'yxatni yangilash
    products = await db.get_products_by_category(cat_id)
    cat = await db.get_category(cat_id)
    cat_name = cat["name"] if cat else "Toifa"

    if not products:
        text = f"📂 <b>{cat_name}</b> toifasida hali mahsulot yo'q."
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Yangi mahsulot qo'shish", callback_data="admin_add_product")],
            [InlineKeyboardButton(text="⬅️ Ortga", callback_data="admin_products")]
        ])
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
        return

    text = f"📂 <b>{cat_name}</b> mahsulotlari:\n\nMahsulotni o'chirish uchun 🗑 tugmasini bosing:"
    markup = admin_category_products_keyboard(cat_id, products)
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)


# --- YANGI MAHSULOT QO'SHISH BOSQICHLARI ---

@router.callback_query(F.data == "admin_add_product")
async def start_add_product(callback: CallbackQuery, state: FSMContext):
    """Mahsulot qo'shish uchun toifa tanlash"""
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    await callback.answer()
    cats = await db.get_categories()
    if not cats:
        await callback.answer("⚠️ Avval kamida bitta kategoriya yarating!", show_alert=True)
        return

    buttons = []
    for c in cats:
        buttons.append([InlineKeyboardButton(text=c["name"], callback_data=f"admin_selcat_{c['id']}")])
    buttons.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_products")])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(
        "➕ <b>Yangi mahsulot qo'shish:</b>\n\nMahsulot qaysi toifaga tegishli ekanligini tanlang:",
        parse_mode="HTML",
        reply_markup=markup
    )


@router.callback_query(F.data.startswith("admin_selcat_"))
async def product_category_selected(callback: CallbackQuery, state: FSMContext):
    """Kategoriya tanlandi, nomini so'rash"""
    cat_id = int(callback.data.split("_")[2])
    await state.update_data(category_id=cat_id)
    await state.set_state(AddProductState.waiting_for_name)
    await callback.answer()

    cancel_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_products")]
    ])
    await callback.message.edit_text(
        "📝 <b>Mahsulot nomini kiriting:</b>\n<i>(Masalan: Samsung Galaxy A55 128GB)</i>",
        parse_mode="HTML",
        reply_markup=cancel_markup
    )


@router.message(AddProductState.waiting_for_name, F.text)
async def process_product_name(message: Message, state: FSMContext):
    """Mahsulot nomi qabul qilindi, tavsifini so'rash"""
    user_id = message.from_user.id if message.from_user else 0
    if not is_admin(user_id):
        return

    name = message.text.strip()
    await state.update_data(name=name)
    await state.set_state(AddProductState.waiting_for_description)

    await message.answer(
        f"✅ Nomi: <b>{name}</b>\n\n"
        "Endi mahsulot haqida qisqacha <b>tavsif (xususiyatlari)</b> kiriting:\n"
        "<i>(Masalan: 8GB RAM, 128GB Xotira, 5000 mAh batareya)</i>",
        parse_mode="HTML"
    )


@router.message(AddProductState.waiting_for_description, F.text)
async def process_product_desc(message: Message, state: FSMContext):
    """Mahsulot tavsifi qabul qilindi, narxini so'rash"""
    user_id = message.from_user.id if message.from_user else 0
    if not is_admin(user_id):
        return

    desc = message.text.strip()
    await state.update_data(description=desc)
    await state.set_state(AddProductState.waiting_for_price)

    await message.answer(
        "💰 Endi mahsulot <b>narxini</b> so'mda kiriting (faqat sonlar bilan):\n"
        "<i>(Masalan: 3500000 yoki 120000)</i>",
        parse_mode="HTML"
    )


@router.message(AddProductState.waiting_for_price, F.text)
async def process_product_price(message: Message, state: FSMContext):
    """Mahsulot narxi qabul qilindi, rasmini so'rash"""
    user_id = message.from_user.id if message.from_user else 0
    if not is_admin(user_id):
        return

    raw_price = message.text.strip().replace(" ", "").replace("so'm", "").replace("som", "")
    try:
        price = float(raw_price)
        if price <= 0:
            raise ValueError()
    except ValueError:
        await message.answer("⚠️ Iltimos, narxni to'g'ri musbat son ko'rinishida kiriting (masalan: 250000):")
        return

    await state.update_data(price=price)
    await state.set_state(AddProductState.waiting_for_image)

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ Rasmsiz davom etish", callback_data="admin_skip_image")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_products")]
    ])
    await message.answer(
        f"💰 Narxi: <b>{format_currency(price)}</b>\n\n"
        "📸 Endi mahsulot <b>rasmini</b> yuboring:\n"
        "Agar rasm qo'shmoqchi bo'lmasangiz, quyidagi tugmani bosing:",
        parse_mode="HTML",
        reply_markup=markup
    )


@router.message(AddProductState.waiting_for_image, F.photo)
async def process_product_image(message: Message, state: FSMContext):
    """Mahsulot rasmi yuborilganda uni saqlash"""
    user_id = message.from_user.id if message.from_user else 0
    if not is_admin(user_id):
        return

    photo_id = message.photo[-1].file_id
    await finalize_add_product(message, state, image_id=photo_id)


@router.callback_query(AddProductState.waiting_for_image, F.data == "admin_skip_image")
async def process_product_skip_image(callback: CallbackQuery, state: FSMContext):
    """Rasmsiz saqlash"""
    await callback.answer()
    await finalize_add_product(callback.message, state, image_id="")


async def finalize_add_product(message: Message, state: FSMContext, image_id: str):
    """Mahsulotni bazaga saqlash va yakunlash"""
    data = await state.get_data()
    category_id = data["category_id"]
    name = data["name"]
    description = data["description"]
    price = data["price"]

    prod_id = await db.add_product(
        category_id=category_id,
        name=name,
        description=description,
        price=price,
        image=image_id
    )
    await state.clear()

    success_text = (
        "🎉 <b>Mahsulot muvaffaqiyatli qo'shildi!</b>\n\n"
        f"🆔 ID: #{prod_id}\n"
        f"🏷 Nomi: <b>{name}</b>\n"
        f"📝 Tavsifi: {description}\n"
        f"💰 Narxi: <b>{format_currency(price)}</b>\n"
        f"📸 Rasm: {'Mavjud' if image_id else 'Rasmsiz'}"
    )

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yana mahsulot qo'shish", callback_data="admin_add_product")],
        [InlineKeyboardButton(text="⬅️ Mahsulotlar bo'limiga", callback_data="admin_products")],
        [InlineKeyboardButton(text="🏠 Admin panel", callback_data="admin_main")]
    ])

    await message.answer(success_text, parse_mode="HTML", reply_markup=markup)
