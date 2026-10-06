from aiogram import Router, F
from aiogram.types import Message
from database import db
from utils.helpers import format_currency, get_status_text

router = Router()


@router.message(F.text == "📦 Buyurtmalarim")
async def show_my_orders(message: Message):
    """Foydalanuvchining o'z buyurtmalari tarixi"""
    user_id = message.from_user.id
    orders = await db.get_user_orders(user_id, limit=5)

    if not orders:
        await message.answer(
            "📦 <b>Sizda hali birorta ham buyurtma mavjud emas.</b>\n\n"
            "Katalogdan mahsulotlarni tanlab, birinchi buyurtmangizni bering!",
            parse_mode="HTML"
        )
        return

    text = "📦 <b>Sizning so'nggi buyurtmalaringiz:</b>\n\n"
    for order in orders:
        items = await db.get_order_items(order["id"])
        items_desc = ", ".join([f"{it['product_name']} ({it['quantity']}x)" for it in items])

        text += (
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>Buyurtma #{order['id']}</b>\n"
            f"📅 Sana: {order['created_at'][:16]}\n"
            f"📊 Holati: <b>{get_status_text(order['status'])}</b>\n"
            f"📦 Mahsulotlar: {items_desc if items_desc else '—'}\n"
            f"💰 Jami summa: <b>{format_currency(order['total_price'])}</b>\n"
        )

    await message.answer(text, parse_mode="HTML")
