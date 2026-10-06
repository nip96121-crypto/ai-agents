from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from database import db
from keyboards import cart_keyboard, empty_cart_keyboard
from utils.helpers import format_currency

router = Router()


def build_cart_text(items: list) -> str:
    """Savatcha xabari matnini shakllantirish"""
    text = "🛒 <b>Sizning savatchangiz:</b>\n\n"
    total_sum = 0
    for idx, item in enumerate(items, 1):
        subtotal = item["quantity"] * item["price"]
        total_sum += subtotal
        text += (
            f"<b>{idx}. {item['name']}</b>\n"
            f"   └ {item['quantity']} dona × {format_currency(item['price'])} = <b>{format_currency(subtotal)}</b>\n"
        )

    text += f"\n━━━━━━━━━━━━━━━━━━━━\n"
    text += f"💰 <b>Jami to'lov miqdori: {format_currency(total_sum)}</b>\n\n"
    text += "Tugmalar yordamida mahsulotlar sonini o'zgartirishingiz yoki buyurtma berishingiz mumkin:"
    return text


@router.message(F.text == "🛒 Savatcha")
async def show_cart_message(message: Message):
    """Savatcha tugmasi bosilganda"""
    user_id = message.from_user.id
    items = await db.get_cart(user_id)

    if not items:
        await message.answer(
            "🛒 <b>Savatchangiz hozircha bo'sh!</b>\n\nKatalogdan o'zingizga yoqqan mahsulotlarni tanlang.",
            parse_mode="HTML",
            reply_markup=empty_cart_keyboard()
        )
        return

    text = build_cart_text(items)
    await message.answer(text, parse_mode="HTML", reply_markup=cart_keyboard(items))


@router.callback_query(F.data == "view_cart")
async def show_cart_callback(callback: CallbackQuery):
    """Inline tugma orqali savatchani ko'rish"""
    await callback.answer()
    user_id = callback.from_user.id
    items = await db.get_cart(user_id)

    if not items:
        text = "🛒 <b>Savatchangiz hozircha bo'sh!</b>\n\nKatalogdan o'zingizga yoqqan mahsulotlarni tanlang."
        try:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=empty_cart_keyboard())
        except Exception:
            await callback.message.delete()
            await callback.message.answer(text, parse_mode="HTML", reply_markup=empty_cart_keyboard())
        return

    text = build_cart_text(items)
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=cart_keyboard(items))
    except Exception:
        await callback.message.delete()
        await callback.message.answer(text, parse_mode="HTML", reply_markup=cart_keyboard(items))


@router.callback_query(F.data.startswith("cart_inc_"))
async def cart_increment(callback: CallbackQuery):
    """Savatchadagi mahsulot sonini 1 taga oshirish"""
    product_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    items = await db.get_cart(user_id)
    current_item = next((item for item in items if item["product_id"] == product_id), None)
    if current_item:
        await db.update_cart_quantity(user_id, product_id, current_item["quantity"] + 1)

    await callback.answer()
    await refresh_cart_message(callback)


@router.callback_query(F.data.startswith("cart_dec_"))
async def cart_decrement(callback: CallbackQuery):
    """Savatchadagi mahsulot sonini 1 taga kamaytirish"""
    product_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    items = await db.get_cart(user_id)
    current_item = next((item for item in items if item["product_id"] == product_id), None)
    if current_item:
        new_qty = current_item["quantity"] - 1
        await db.update_cart_quantity(user_id, product_id, new_qty)

    await callback.answer()
    await refresh_cart_message(callback)


@router.callback_query(F.data.startswith("cart_del_"))
async def cart_delete_item(callback: CallbackQuery):
    """Mahsulotni savatchadan butunlay o'chirish"""
    product_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    await db.remove_from_cart(user_id, product_id)
    await callback.answer("🗑 Mahsulot savatchadan olib tashlandi.")
    await refresh_cart_message(callback)


@router.callback_query(F.data == "clear_cart")
async def clear_cart_handler(callback: CallbackQuery):
    """Savatchani butunlay tozalash"""
    user_id = callback.from_user.id
    await db.clear_cart(user_id)
    await callback.answer("🧹 Savatchangiz tozalandi.")
    text = "🛒 <b>Savatchangiz bo'shatildi!</b>"
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=empty_cart_keyboard())
    except Exception:
        await callback.message.delete()
        await callback.message.answer(text, parse_mode="HTML", reply_markup=empty_cart_keyboard())


async def refresh_cart_message(callback: CallbackQuery):
    """Savatcha o'zgarganda xabarni yangilash"""
    user_id = callback.from_user.id
    items = await db.get_cart(user_id)

    if not items:
        text = "🛒 <b>Savatchangiz bo'sh!</b>"
        try:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=empty_cart_keyboard())
        except Exception:
            await callback.message.delete()
            await callback.message.answer(text, parse_mode="HTML", reply_markup=empty_cart_keyboard())
        return

    text = build_cart_text(items)
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=cart_keyboard(items))
    except Exception:
        await callback.message.delete()
        await callback.message.answer(text, parse_mode="HTML", reply_markup=cart_keyboard(items))
