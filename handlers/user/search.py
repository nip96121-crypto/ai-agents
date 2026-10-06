from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from database import db
from states.user_states import SearchState
from keyboards import cancel_keyboard, main_menu_keyboard
from utils.helpers import format_currency
from config import is_admin

router = Router()


@router.message(F.text == "🔍 Mahsulot qidirish")
async def start_search(message: Message, state: FSMContext):
    """Qidiruvni boshlash"""
    await state.set_state(SearchState.waiting_for_query)
    await message.answer(
        "🔍 <b>Mahsulot qidirish:</b>\n\n"
        "Qidirayotgan mahsulotingiz nomini yoki kalit so'zni yozib yuboring:\n"
        "<i>(Masalan: iPhone, AirPods, Noutbuk...)</i>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )


@router.message(SearchState.waiting_for_query, F.text)
async def process_search_query(message: Message, state: FSMContext):
    """Qidiruv natijalarini chiqarish"""
    query = message.text.strip()
    if query == "❌ Bekor qilish":
        await state.clear()
        user_id = message.from_user.id if message.from_user else 0
        await message.answer("Qidiruv bekor qilindi.", reply_markup=main_menu_keyboard(is_admin_user=is_admin(user_id)))
        return

    products = await db.search_products(query)
    await state.clear()
    user_id = message.from_user.id if message.from_user else 0

    if not products:
        await message.answer(
            f"🔍 <i>«{query}»</i> bo'yicha hech qanday mahsulot topilmadi.",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(is_admin_user=is_admin(user_id))
        )
        return

    buttons = []
    for p in products:
        text = f"{p['name']} | {format_currency(p['price'])}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"prod_{p['id']}")])

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(
        f"🔍 <i>«{query}»</i> so'rovi bo'yicha topilgan mahsulotlar:\n\nBatafsil ko'rish uchun tanlang:",
        parse_mode="HTML",
        reply_markup=markup
    )
    await message.answer("Asosiy menyu:", reply_markup=main_menu_keyboard(is_admin_user=is_admin(user_id)))
