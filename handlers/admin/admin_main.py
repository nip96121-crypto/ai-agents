from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import is_admin
from database import db
from keyboards import admin_main_keyboard
from utils.helpers import format_currency

router = Router()


@router.message(Command("admin"))
@router.message(F.text == "🔐 Admin Panel")
async def cmd_admin(message: Message, state: FSMContext):
    """Admin paneliga kirish"""
    await state.clear()
    user_id = message.from_user.id if message.from_user else 0

    if not is_admin(user_id):
        await message.answer("⛔️ Kechirasiz, sizda ushbu bo'limga kirish huquqi yo'q.")
        return

    text = (
        "🔐 <b>Boshqaruv Paneli (Admin Panel)</b>\n\n"
        "Quyidagi bo'limlardan birini tanlang:"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=admin_main_keyboard())


@router.callback_query(F.data == "admin_main")
async def admin_main_callback(callback: CallbackQuery, state: FSMContext):
    """Admin panel bosh sahifasiga qaytish"""
    await state.clear()
    user_id = callback.from_user.id

    if not is_admin(user_id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    await callback.answer()
    text = (
        "🔐 <b>Boshqaruv Paneli (Admin Panel)</b>\n\n"
        "Quyidagi bo'limlardan birini tanlang:"
    )
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=admin_main_keyboard())
    except Exception:
        await callback.message.delete()
        await callback.message.answer(text, parse_mode="HTML", reply_markup=admin_main_keyboard())


@router.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery):
    """Do'kon statistikasi"""
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    await callback.answer()
    stats = await db.get_statistics()

    text = (
        "📊 <b>DO'KON STATISTIKASI:</b>\n\n"
        f"👥 <b>Foydalanuvchilar soni:</b> {stats['users_count']} nafar\n"
        f"🛍 <b>Faol mahsulotlar:</b> {stats['products_count']} ta\n"
        f"📦 <b>Jami buyurtmalar:</b> {stats['orders_count']} ta\n"
        f"⏳ <b>Kutilayotgan yangi buyurtmalar:</b> {stats['pending_orders']} ta\n"
        f"💰 <b>Umumiy yakunlangan savdo:</b> {format_currency(stats['total_revenue'])}\n"
    )

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Admin panelga qaytish", callback_data="admin_main")]
    ])
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
