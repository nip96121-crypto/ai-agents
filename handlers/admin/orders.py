from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import is_admin
from database import db
from keyboards import admin_orders_list_keyboard, admin_order_actions_keyboard
from utils.helpers import format_currency, get_status_text

router = Router()


@router.callback_query(F.data == "admin_orders")
async def show_orders_list(callback: CallbackQuery):
    """Admin: buyurtmalar ro'yxatini ko'rish"""
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    await callback.answer()
    orders = await db.get_orders(limit=15)

    if not orders:
        text = "📦 <b>Hozircha hech qanday buyurtma mavjud emas.</b>"
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Admin panelga qaytish", callback_data="admin_main")]
        ])
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
        return

    text = "📦 <b>So'nggi buyurtmalar ro'yxati:</b>\n\nBatafsil ko'rish uchun buyurtmani tanlang:"
    markup = admin_orders_list_keyboard(orders)
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
    except Exception:
        await callback.message.delete()
        await callback.message.answer(text, parse_mode="HTML", reply_markup=markup)


@router.callback_query(F.data.startswith("admin_order_"))
async def show_order_detail_admin(callback: CallbackQuery):
    """Buyurtma tafsilotlarini ko'rish"""
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    await callback.answer()
    order_id = int(callback.data.split("_")[2])
    order = await db.get_order(order_id)

    if not order:
        await callback.answer("❌ Buyurtma topilmadi!", show_alert=True)
        return

    items = await db.get_order_items(order_id)

    text = (
        f"📋 <b>BUYURTMA #{order['id']} TAFSILOTLARI:</b>\n\n"
        f"📅 <b>Sana:</b> {order['created_at'][:16]}\n"
        f"📊 <b>Holati:</b> {get_status_text(order['status'])}\n"
        f"👤 <b>Mijoz:</b> {order['customer_name']}\n"
        f"📞 <b>Telefon:</b> {order['customer_phone']}\n"
        f"📍 <b>Manzil:</b> {order['address']}\n"
        f"💳 <b>To'lov turi:</b> {order['payment_method']}\n\n"
        f"📦 <b>Mahsulotlar tarkibi:</b>\n"
    )

    for idx, it in enumerate(items, 1):
        subtotal = it["quantity"] * it["price"]
        text += f"{idx}. {it['product_name']} — {it['quantity']} dona × {format_currency(it['price'])} = {format_currency(subtotal)}\n"

    text += f"\n💰 <b>JAMI SUMMA: {format_currency(order['total_price'])}</b>\n\n"
    text += "Buyurtma holatini quyidagi tugmalar yordamida o'zgartirishingiz mumkin:"

    markup = admin_order_actions_keyboard(order_id, order["status"])
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)


@router.callback_query(F.data.startswith("status_"))
async def change_order_status(callback: CallbackQuery, bot: Bot):
    """Buyurtma holatini o'zgartirish va mijozga bildirishnoma yuborish"""
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    parts = callback.data.split("_")
    order_id = int(parts[1])
    new_status = parts[2]

    order = await db.get_order(order_id)
    if not order:
        await callback.answer("❌ Buyurtma topilmadi!", show_alert=True)
        return

    # Holatni yangilash
    await db.update_order_status(order_id, new_status)
    status_text = get_status_text(new_status)

    await callback.answer(f"✅ Holat o'zgartirildi: {status_text}", show_alert=True)

    # Mijozga avtomatik bildirishnoma yuborish
    customer_id = order["user_id"]
    customer_msg = (
        f"🔔 <b>Buyurtmangiz holati yangilandi!</b>\n\n"
        f"🆔 <b>Buyurtma:</b> #{order_id}\n"
        f"📊 <b>Yangi holati:</b> <b>{status_text}</b>\n\n"
    )

    if new_status == "confirmed":
        customer_msg += "Buyurtmangiz tasdiqlandi va mutaxassislarimiz uni yetkazib berishga tayyorlamoqda."
    elif new_status == "shipping":
        customer_msg += "Buyurtmangiz kuryerga topshirildi va yetkazib berilmoqda. Tez orada yetib boradi!"
    elif new_status == "completed":
        customer_msg += "Buyurtmangiz muvaffaqiyatli topshirildi va yakunlandi. Bizni tanlaganingiz uchun tashakkur! 😊"
    elif new_status == "cancelled":
        customer_msg += "Afsuski, buyurtmangiz bekor qilindi. Batafsil ma'lumot uchun qo'llab-quvvatlash xizmatiga murojaat qiling."

    try:
        await bot.send_message(chat_id=customer_id, text=customer_msg, parse_mode="HTML")
    except Exception:
        pass

    # Admin xabarini yangilash
    items = await db.get_order_items(order_id)
    text = (
        f"📋 <b>BUYURTMA #{order['id']} TAFSILOTLARI:</b>\n\n"
        f"📅 <b>Sana:</b> {order['created_at'][:16]}\n"
        f"📊 <b>Holati:</b> <b>{status_text}</b>\n"
        f"👤 <b>Mijoz:</b> {order['customer_name']}\n"
        f"📞 <b>Telefon:</b> {order['customer_phone']}\n"
        f"📍 <b>Manzil:</b> {order['address']}\n"
        f"💳 <b>To'lov turi:</b> {order['payment_method']}\n\n"
        f"📦 <b>Mahsulotlar tarkibi:</b>\n"
    )
    for idx, it in enumerate(items, 1):
        subtotal = it["quantity"] * it["price"]
        text += f"{idx}. {it['product_name']} — {it['quantity']} dona × {format_currency(it['price'])} = {format_currency(subtotal)}\n"

    text += f"\n💰 <b>JAMI SUMMA: {format_currency(order['total_price'])}</b>\n\n"
    text += "✅ Holat yangilandi va mijozga bildirishnoma yuborildi."

    markup = admin_order_actions_keyboard(order_id, new_status)
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
    except Exception:
        pass
