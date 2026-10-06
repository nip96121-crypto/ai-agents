from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from database import db
from states.user_states import OrderState
from keyboards import (
    phone_request_keyboard,
    location_request_keyboard,
    payment_methods_keyboard,
    order_confirmation_keyboard,
    main_menu_keyboard,
    cancel_keyboard,
    admin_order_actions_keyboard
)
from utils.helpers import format_currency, get_status_text
from config import ADMIN_IDS, is_admin

router = Router()


@router.callback_query(F.data == "checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    """Buyurtma rasmiylashtirishni boshlash"""
    await callback.answer()
    user_id = callback.from_user.id
    items = await db.get_cart(user_id)

    if not items:
        await callback.answer("Savatchangiz bo'sh!", show_alert=True)
        return

    # Foydalanuvchi ma'lumotlarini tekshirish
    user_data = await db.get_user(user_id)
    default_name = callback.from_user.full_name or ""

    await state.set_state(OrderState.waiting_for_name)
    await state.update_data(items=items)

    text = (
        "📝 <b>Buyurtma rasmiylashtirish (1/4):</b>\n\n"
        f"Iltimos, to'liq ism-familiyangizni kiriting:\n"
        f"<i>(Masalan: {default_name})</i>"
    )
    await callback.message.answer(text, parse_mode="HTML", reply_markup=cancel_keyboard())


@router.message(OrderState.waiting_for_name, F.text)
async def process_name(message: Message, state: FSMContext):
    """Ismni qabul qilish va telefon so'rash"""
    name = message.text.strip()
    if len(name) < 3:
        await message.answer("⚠️ Iltimos, ism va familiyangizni to'liqroq kiriting:")
        return

    await state.update_data(name=name)
    await state.set_state(OrderState.waiting_for_phone)

    await message.answer(
        "📱 <b>Bog'lanish uchun telefon raqamingiz (2/4):</b>\n\n"
        "Quyidagi <b>«📱 Telefon raqamni yuborish»</b> tugmasini bosing yoki raqamingizni yozib qoldiring (+998901234567):",
        parse_mode="HTML",
        reply_markup=phone_request_keyboard()
    )


@router.message(OrderState.waiting_for_phone, F.contact)
@router.message(OrderState.waiting_for_phone, F.text)
async def process_phone(message: Message, state: FSMContext):
    """Telefon raqamni qabul qilish va manzil so'rash"""
    if message.contact:
        phone = message.contact.phone_number
        if not phone.startswith("+"):
            phone = "+" + phone
    else:
        phone = message.text.strip()
        # Oddiy tekshirish
        digits = [c for c in phone if c.isdigit()]
        if len(digits) < 7:
            await message.answer("⚠️ Telefon raqam noto'g'ri ko'rinadi. Iltimos, qaytadan kiriting:")
            return

    await state.update_data(phone=phone)
    if message.from_user:
        await db.update_user_phone(message.from_user.id, phone)

    await state.set_state(OrderState.waiting_for_address)

    await message.answer(
        "📍 <b>Yetkazib berish manzili (3/4):</b>\n\n"
        "Yetkazib berish oson bo'lishi uchun joylashuvingizni (geolokatsiya) yuboring "
        "yoki manzilingizni yozib yuboring (Shahar, tuman, ko'cha, uy):",
        parse_mode="HTML",
        reply_markup=location_request_keyboard()
    )


@router.message(OrderState.waiting_for_address, F.location)
@router.message(OrderState.waiting_for_address, F.text)
async def process_address(message: Message, state: FSMContext):
    """Manzil yoki lokatsiyani qabul qilish va to'lov turini so'rash"""
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
        address = "📍 Geolokatsiya orqali yuborildi"
        await state.update_data(address=address, latitude=lat, longitude=lon)
    else:
        addr_text = message.text.strip()
        if addr_text == "✍️ Manzilni qo'lda yozish":
            await message.answer("Iltimos, aniq manzilingizni yozing:")
            return
        await state.update_data(address=addr_text, latitude=None, longitude=None)

    await state.set_state(OrderState.waiting_for_payment)

    await message.answer(
        "💳 <b>To'lov turini tanlang (4/4):</b>\n\n"
        "O'zingizga qulay bo'lgan to'lov usulini tanlang:",
        parse_mode="HTML",
        reply_markup=payment_methods_keyboard()
    )


@router.callback_query(OrderState.waiting_for_payment, F.data.in_(["pay_cash", "pay_card"]))
async def process_payment(callback: CallbackQuery, state: FSMContext):
    """To'lov turini tanlash va buyurtma xulosasini ko'rsatish"""
    await callback.answer()
    payment_method = "💵 Naqd pul (Qabul qilinganda)" if callback.data == "pay_cash" else "💳 Plastik karta (Click / Payme)"
    await state.update_data(payment_method=payment_method)

    data = await state.get_data()
    items = data.get("items", [])
    total_price = sum(item["quantity"] * item["price"] for item in items)

    summary = (
        "📋 <b>BUYURTMANI TASDIQLASH:</b>\n\n"
        f"👤 <b>Qabul qiluvchi:</b> {data.get('name')}\n"
        f"📞 <b>Telefon:</b> {data.get('phone')}\n"
        f"📍 <b>Manzil:</b> {data.get('address')}\n"
        f"💳 <b>To'lov usuli:</b> {payment_method}\n\n"
        "🛒 <b>Mahsulotlar:</b>\n"
    )

    for idx, item in enumerate(items, 1):
        subtotal = item["quantity"] * item["price"]
        summary += f"{idx}. {item['name']} — {item['quantity']} dona × {format_currency(item['price'])} = {format_currency(subtotal)}\n"

    summary += f"\n💰 <b>JAMI TO'LOV: {format_currency(total_price)}</b>\n\n"
    summary += "Barcha ma'lumotlar to'g'rimi? Tasdiqlaysizmi?"

    await state.set_state(OrderState.waiting_for_confirmation)
    await callback.message.edit_text(summary, parse_mode="HTML", reply_markup=order_confirmation_keyboard())


@router.callback_query(F.data == "cancel_order")
@router.callback_query(OrderState.waiting_for_confirmation, F.data == "confirm_order_no")
async def cancel_order_flow(callback: CallbackQuery, state: FSMContext):
    """Buyurtmani bekor qilish"""
    await state.clear()
    await callback.answer("Buyurtma bekor qilindi.")
    user_id = callback.from_user.id
    await callback.message.delete()
    await callback.message.answer(
        "❌ Buyurtma berish bekor qilindi.",
        reply_markup=main_menu_keyboard(is_admin_user=is_admin(user_id))
    )


@router.callback_query(OrderState.waiting_for_confirmation, F.data == "confirm_order_yes")
async def confirm_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Buyurtmani bazaga saqlash va adminga xabar yuborish"""
    await callback.answer()
    data = await state.get_data()
    user_id = callback.from_user.id

    items = data.get("items", [])
    if not items:
        # Baza orqali tekshirish
        items = await db.get_cart(user_id)

    total_price = sum(item["quantity"] * item["price"] for item in items)

    name = data.get("name", callback.from_user.full_name)
    phone = data.get("phone", "")
    address = data.get("address", "")
    lat = data.get("latitude")
    lon = data.get("longitude")
    payment_method = data.get("payment_method", "Naqd pul")

    # Bazaga yozish
    order_id = await db.create_order(
        user_id=user_id,
        total_price=total_price,
        customer_name=name,
        customer_phone=phone,
        address=address,
        latitude=lat,
        longitude=lon,
        payment_method=payment_method,
        items=items
    )

    await state.clear()
    await callback.message.delete()

    # Foydalanuvchiga muvaffaqiyat xabari
    success_text = (
        f"🎉 <b>Buyurtmangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"🆔 <b>Buyurtma raqami:</b> #{order_id}\n"
        f"💰 <b>Jami summa:</b> {format_currency(total_price)}\n"
        f"⏳ <b>Holati:</b> {get_status_text('pending')}\n\n"
        "Tez orada operatorimiz siz bilan bog'lanadi va yetkazib berish tafsilotlarini aniqlaydi. "
        "Buyurtmalaringiz holatini «📦 Buyurtmalarim» bo'limida kuzatib borishingiz mumkin."
    )
    await callback.message.answer(
        success_text,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin_user=is_admin(user_id))
    )

    # ADMINLARGA BILDIRISHNOMA YUBORISH
    admin_notif_text = (
        f"🚨 <b>YANGI BUYURTMA #{order_id}!</b>\n\n"
        f"👤 <b>Mijoz:</b> {name} (@{callback.from_user.username or 'username_yoq'})\n"
        f"📞 <b>Telefon:</b> {phone}\n"
        f"📍 <b>Manzil:</b> {address}\n"
        f"💳 <b>To'lov turi:</b> {payment_method}\n\n"
        f"📦 <b>Buyurtma tarkibi:</b>\n"
    )
    for idx, item in enumerate(items, 1):
        admin_notif_text += f"{idx}. {item['name']} — {item['quantity']} dona × {format_currency(item['price'])}\n"

    admin_notif_text += f"\n💰 <b>Jami: {format_currency(total_price)}</b>"

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=admin_notif_text,
                parse_mode="HTML",
                reply_markup=admin_order_actions_keyboard(order_id, "pending")
            )
            # Agar foydalanuvchi joylashuv yuborgan bo'lsa, adminga lokatsiya xaritasi yuborish
            if lat and lon:
                await bot.send_location(chat_id=admin_id, latitude=lat, longitude=lon)
        except Exception as e:
            # Agar admin botni start qilmagan bo'lsa xatolikni chetlab o'tamiz
            pass
