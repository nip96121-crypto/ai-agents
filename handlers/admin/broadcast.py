import asyncio
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from config import is_admin
from database import db
from states.admin_states import BroadcastState

router = Router()


@router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    """Rassilka (xabar tarqatish) jarayonini boshlash"""
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    await callback.answer()
    await state.set_state(BroadcastState.waiting_for_message)

    cancel_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_main")]
    ])

    await callback.message.edit_text(
        "📢 <b>Barcha foydalanuvchilarga xabar tarqatish (Rassilka):</b>\n\n"
        "Foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yuboring (matn yoki rasm):",
        parse_mode="HTML",
        reply_markup=cancel_markup
    )


@router.message(BroadcastState.waiting_for_message, F.text)
@router.message(BroadcastState.waiting_for_message, F.photo)
async def receive_broadcast_content(message: Message, state: FSMContext):
    """Tarqatiladigan xabarni qabul qilish va tasdiq so'rash"""
    user_id = message.from_user.id if message.from_user else 0
    if not is_admin(user_id):
        return

    if message.photo:
        photo_id = message.photo[-1].file_id
        caption = message.caption or ""
        await state.update_data(type="photo", photo_id=photo_id, caption=caption)
    else:
        await state.update_data(type="text", text=message.text)

    await state.set_state(BroadcastState.waiting_for_confirm)

    users_count = await db.get_users_count()
    confirm_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚀 Ha, barchaga yuborilsin", callback_data="confirm_broadcast_yes"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_main")
        ]
    ])

    await message.answer(
        f"⚠️ <b>Tasdiqlash:</b>\n\nUshbu xabar bazadagi jami <b>{users_count} nafar</b> foydalanuvchiga yuboriladi.\nTasdiqlaysizmi?",
        parse_mode="HTML",
        reply_markup=confirm_markup
    )


@router.callback_query(BroadcastState.waiting_for_confirm, F.data == "confirm_broadcast_yes")
async def send_broadcast(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Xabarni barcha foydalanuvchilarga jo'natish"""
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    await callback.answer()
    data = await state.get_data()
    await state.clear()

    user_ids = await db.get_all_user_ids()
    await callback.message.edit_text("⏳ Xabar tarqatilmoqda, iltimos kuting...")

    success_count = 0
    fail_count = 0

    msg_type = data.get("type", "text")
    for u_id in user_ids:
        try:
            if msg_type == "photo":
                await bot.send_photo(chat_id=u_id, photo=data["photo_id"], caption=data.get("caption", ""), parse_mode="HTML")
            else:
                await bot.send_message(chat_id=u_id, text=data["text"], parse_mode="HTML")
            success_count += 1
            await asyncio.sleep(0.05)  # Telegram flood limit oldini olish
        except Exception:
            fail_count += 1

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Admin panelga qaytish", callback_data="admin_main")]
    ])

    report = (
        "📢 <b>Xabar tarqatish yakunlandi!</b>\n\n"
        f"✅ Muvaffaqiyatli yetkazildi: <b>{success_count} ta</b>\n"
        f"❌ Yetib bormadi (bloklagan yoki nofaol): <b>{fail_count} ta</b>"
    )
    await callback.message.edit_text(report, parse_mode="HTML", reply_markup=markup)
