from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from config import is_admin
from database import db
from states.admin_states import AddCategoryState
from keyboards import admin_categories_keyboard

router = Router()


@router.callback_query(F.data == "admin_categories")
async def show_categories(callback: CallbackQuery, state: FSMContext):
    """Kategoriyalar ro'yxatini ko'rsatish"""
    await state.clear()
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    await callback.answer()
    cats = await db.get_categories()
    text = (
        "🗂 <b>Kategoriyalar boshqaruvi:</b>\n\n"
        "Yangi kategoriya qo'shishingiz yoki mavjudini o'chirishingiz mumkin:\n"
        "<i>(Eslatma: Kategoriya o'chirilsa, unga tegishli barcha mahsulotlar ham o'chiriladi)</i>"
    )
    markup = admin_categories_keyboard(cats)
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
    except Exception:
        await callback.message.delete()
        await callback.message.answer(text, parse_mode="HTML", reply_markup=markup)


@router.callback_query(F.data == "admin_add_category")
async def add_category_start(callback: CallbackQuery, state: FSMContext):
    """Yangi kategoriya qo'shish jarayonini boshlash"""
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    await callback.answer()
    await state.set_state(AddCategoryState.waiting_for_name)

    cancel_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_categories")]
    ])
    await callback.message.edit_text(
        "➕ <b>Yangi kategoriya qo'shish:</b>\n\n"
        "Kategoriya nomini kiriting:\n"
        "<i>(Masalan: 📱 Smartfonlar, 👟 Poyabzallar)</i>",
        parse_mode="HTML",
        reply_markup=cancel_markup
    )


@router.message(AddCategoryState.waiting_for_name, F.text)
async def process_category_name(message: Message, state: FSMContext):
    """Kategoriya nomini saqlash"""
    user_id = message.from_user.id if message.from_user else 0
    if not is_admin(user_id):
        return

    cat_name = message.text.strip()
    if len(cat_name) < 2:
        await message.answer("⚠️ Kategoriya nomi juda qisqa. Qaytadan kiriting:")
        return

    try:
        await db.add_category(cat_name)
        await state.clear()
        cats = await db.get_categories()
        await message.answer(
            f"✅ <b>«{cat_name}»</b> kategoriyasi muvaffaqiyatli qo'shildi!",
            parse_mode="HTML",
            reply_markup=admin_categories_keyboard(cats)
        )
    except Exception as e:
        await message.answer(f"⚠️ Xatolik yuz berdi (ehtimol bunday nomli kategoriya allaqachon mavjud): {e}")


@router.callback_query(F.data.startswith("admin_del_cat_"))
async def delete_category(callback: CallbackQuery):
    """Kategoriyani o'chirish"""
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    cat_id = int(callback.data.split("_")[3])
    cat = await db.get_category(cat_id)
    cat_name = cat["name"] if cat else "Kategoriya"

    await db.delete_category(cat_id)
    await callback.answer(f"🗑 «{cat_name}» va uning mahsulotlari o'chirildi!", show_alert=True)

    cats = await db.get_categories()
    text = (
        "🗂 <b>Kategoriyalar boshqaruvi:</b>\n\n"
        "Yangi kategoriya qo'shishingiz yoki mavjudini o'chirishingiz mumkin:"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=admin_categories_keyboard(cats))
