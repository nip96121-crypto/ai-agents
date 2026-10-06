from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from database import db
from keyboards import main_menu_keyboard
from config import is_admin

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Start buyrug'i: foydalanuvchini ro'yxatga olish va asosiy menyuni chiqarish"""
    await state.clear()
    user = message.from_user
    if user:
        await db.add_or_update_user(
            user_id=user.id,
            full_name=user.full_name,
            username=user.username
        )

    admin_status = is_admin(user.id) if user else False

    greeting_text = (
        f"Assalomu alaykum, <b>{user.first_name if user else 'Qadrli mijoz'}</b>! 👋\n\n"
        f"Bizning onlayn do'konimizga xush kelibsiz! ✨\n"
        f"Bu yerda siz o'zingizga ma'qul mahsulotlarni qulay va tez xarid qilishingiz mumkin.\n\n"
        f"Quyidagi menyudan kerakli bo'limni tanlang:"
    )

    await message.answer(
        greeting_text,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin_user=admin_status)
    )


@router.message(F.text == "❌ Bekor qilish")
async def cancel_handler(message: Message, state: FSMContext):
    """Jarayonni bekor qilish"""
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()

    user_id = message.from_user.id if message.from_user else 0
    await message.answer(
        "❌ Jarayon bekor qilindi. Asosiy menyudasiz.",
        reply_markup=main_menu_keyboard(is_admin_user=is_admin(user_id))
    )


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
    """Inline menyudan asosiy menyuga qaytish"""
    await state.clear()
    await callback.answer()
    user_id = callback.from_user.id
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=main_menu_keyboard(is_admin_user=is_admin(user_id))
    )


@router.message(F.text == "ℹ️ Biz haqimizda")
async def about_us(message: Message):
    """Biz haqimizda ma'lumot"""
    about_text = (
        "🏢 <b>Biz haqimizda:</b>\n\n"
        "Bizning onlayn do'konimiz sifatli va kafolatlangan mahsulotlarni eng maqbul narxlarda "
        "taklif etadi. Tezkor yetkazib berish xizmati va doimiy mijozlar uchun chegirmalar mavjud!\n\n"
        "⏰ Ish vaqti: 09:00 - 21:00 (Dam olish kunlarisiz)\n"
        "🚚 Butun O'zbekiston bo'ylab yetkazib berish xizmati mavjud."
    )
    await message.answer(about_text, parse_mode="HTML")


@router.message(F.text == "📞 Aloqa / Yordam")
async def contact_us(message: Message):
    """Bog'lanish ma'lumotlari"""
    contact_text = (
        "📞 <b>Bog'lanish va qo'llab-quvvatlash:</b>\n\n"
        "Savollaringiz yoki takliflaringiz bo'lsa, biz bilan bog'laning:\n\n"
        "☎️ Telefon: +998 (90) 123-45-67\n"
        "💬 Telegram: @shop_admin_support\n"
        "📧 Email: support@onlineshop.uz\n\n"
        "Operatorlarimiz tez orada sizga javob berishadi!"
    )
    await message.answer(contact_text, parse_mode="HTML")
