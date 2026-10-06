from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot import database as db
from bot.config import CURRENCY
from bot.keyboards import (
    main_menu_kb, categories_kb, products_kb, product_detail_kb,
    cart_kb, order_confirm_kb, user_orders_kb,
)
from bot.handlers.admin import admin_main_kb as admin_panel_kb

router = Router()


class OrderState(StatesGroup):
    waiting_address = State()
    waiting_phone = State()


# ─── Start ───────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = db.get_user(message.from_user.id)
    if not user:
        db.save_user(message.from_user.id, {
            "full_name": message.from_user.full_name,
            "username": message.from_user.username or "",
            "first_seen": str(message.date),
        })
    await message.answer(
        f"🛍️ Xush kelibsiz, <b>{message.from_user.full_name}</b>!\n\n"
        "Men online do'kon botman. Quyidagi buyruqlardan foydalaning:",
        reply_markup=main_menu_kb(),
        parse_mode="HTML",
    )

    # ID ni ko'rsatish (admin uchun)
    await message.answer(
        f"🔑 Sizning Telegram ID `ngiz: <code>{message.from_user.id}</code>"
    )


# ─── Main Menu ───────────────────────────────────────────

@router.message(F.text == "📦 Kategoriyalar")
async def show_categories(message: Message):
    await message.answer("📂 Kategoriyalardan birini tanlang:", reply_markup=categories_kb())


@router.callback_query(F.data == "back_to_cats")
async def back_to_cats(callback: CallbackQuery):
    await callback.message.edit_text("📂 Kategoriyalardan birini tanlang:", reply_markup=categories_kb())


@router.callback_query(F.data.startswith("cat:"))
async def show_products(callback: CallbackQuery):
    cat_id = callback.data.split(":")[1]
    cats = db.get_categories()
    cat_name = cats.get(cat_id, {}).get("name", "Noma'lum")
    await callback.message.edit_text(
        f"📦 <b>{cat_name}</b> kategoriyasidagi mahsulotlar:",
        reply_markup=products_kb(cat_id),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "back_to_products")
async def back_to_products(callback: CallbackQuery):
    await callback.message.edit_text("📂 Kategoriyalardan birini tanlang:", reply_markup=categories_kb())


@router.callback_query(F.data.startswith("prod:"))
async def show_product_detail(callback: CallbackQuery):
    pid = callback.data.split(":")[1]
    product = db.get_product(pid)
    if not product:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return
    text = (
        f"🏷️ <b>{product['name']}</b>\n\n"
        f"📝 {product.get('description', 'Tavsif yo\'q')}\n\n"
        f"💰 Narxi: <b>{product['price']:,} {CURRENCY}</b>\n"
        f"📦 Mavjud: {product.get('stock', 0)} dona"
    )
    await callback.message.edit_text(text, reply_markup=product_detail_kb(pid), parse_mode="HTML")


# ─── Cart ────────────────────────────────────────────────

@router.callback_query(F.data.startswith("add_cart:"))
async def add_to_cart(callback: CallbackQuery):
    pid = callback.data.split(":")[1]
    product = db.get_product(pid)
    if not product:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return
    db.add_to_cart(callback.from_user.id, pid, 1)
    await callback.answer(f"✅ {product['name']} savatga qo'shildi!", show_alert=True)


@router.message(F.text == "🛒 Savatim")
async def show_cart(message: Message):
    cart = db.get_cart(message.from_user.id)
    if not cart:
        await message.answer("🛒 Savatingiz bo'sh.\n\nKategoriyalardan xaridni boshlang!", reply_markup=categories_kb())
        return
    total = 0
    text = "🛒 <b>Savatingiz:</b>\n\n"
    for pid, qty in cart.items():
        product = db.get_product(pid)
        if product:
            subtotal = product["price"] * qty
            total += subtotal
            text += f"• {product['name']} x{qty} = {subtotal:,} {CURRENCY}\n"
    text += f"\n💰 <b>Jami: {total:,} {CURRENCY}</b>"
    await message.answer(text, reply_markup=cart_kb(message.from_user.id), parse_mode="HTML")


@router.callback_query(F.data.startswith("cart_plus:"))
async def cart_plus(callback: CallbackQuery):
    pid = callback.data.split(":")[1]
    db.add_to_cart(callback.from_user.id, pid, 1)
    await _refresh_cart(callback)


@router.callback_query(F.data.startswith("cart_minus:"))
async def cart_minus(callback: CallbackQuery):
    pid = callback.data.split(":")[1]
    cart = db.get_cart(callback.from_user.id)
    if cart.get(pid, 0) > 1:
        cart[pid] -= 1
        db.save_cart(callback.from_user.id, cart)
    else:
        db.remove_from_cart(callback.from_user.id, pid)
    await _refresh_cart(callback)


@router.callback_query(F.data.startswith("cart_remove:"))
async def cart_remove(callback: CallbackQuery):
    pid = callback.data.split(":")[1]
    db.remove_from_cart(callback.from_user.id, pid)
    await _refresh_cart(callback)


@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    db.clear_cart(callback.from_user.id)
    await callback.message.edit_text("🗑️ Savat tozalandi!", reply_markup=categories_kb())


async def _refresh_cart(callback: CallbackQuery):
    cart = db.get_cart(callback.from_user.id)
    if not cart:
        await callback.message.edit_text("🛒 Savatingiz bo'sh.", reply_markup=categories_kb())
        return
    total = 0
    text = "🛒 <b>Savatingiz:</b>\n\n"
    for pid, qty in cart.items():
        product = db.get_product(pid)
        if product:
            subtotal = product["price"] * qty
            total += subtotal
            text += f"• {product['name']} x{qty} = {subtotal:,} {CURRENCY}\n"
    text += f"\n💰 <b>Jami: {total:,} {CURRENCY}</b>"
    await callback.message.edit_text(text, reply_markup=cart_kb(callback.from_user.id), parse_mode="HTML")


# ─── Create Order ────────────────────────────────────────

@router.callback_query(F.data == "create_order")
async def create_order(callback: CallbackQuery, state: FSMContext):
    cart = db.get_cart(callback.from_user.id)
    if not cart:
        await callback.answer("Savat bo'sh!", show_alert=True)
        return
    total = 0
    text = "📋 <b>Buyurtma ma'lumotlari:</b>\n\n"
    for pid, qty in cart.items():
        product = db.get_product(pid)
        if product:
            subtotal = product["price"] * qty
            total += subtotal
            text += f"• {product['name']} x{qty} = {subtotal:,} {CURRENCY}\n"
    text += f"\n💰 <b>Jami: {total:,} {CURRENCY}</b>\n\n"
    text += "📍 Yetkazish manzilini kiriting:"
    await callback.message.edit_text(text, parse_mode="HTML")
    await state.set_state(OrderState.waiting_address)
    await state.update_data(total=total, items=cart)


@router.message(OrderState.waiting_address)
async def get_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("📞 Telefon raqamingizni kiriting (masalan: +998901234567):")
    await state.set_state(OrderState.waiting_phone)


@router.message(OrderState.waiting_phone)
async def get_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = f"ord_{message.from_user.id}_{message.date.timestamp():.0f}"
    items = data.get("items", {})
    total = data.get("total", 0)

    db.save_order(order_id, {
        "user_id": message.from_user.id,
        "full_name": message.from_user.full_name,
        "username": message.from_user.username or "",
        "items": items,
        "total": total,
        "address": data.get("address", ""),
        "phone": message.text,
        "status": "pending",
    })

    db.clear_cart(message.from_user.id)

    await message.answer(
        f"✅ <b>Buyurtma qabul qilindi!</b>\n\n"
        f"🆔 Buyurtma ID: <code>{order_id[-6:]}</code>\n"
        f"💰 Jami: {total:,} {CURRENCY}\n"
        f"📍 Manzil: {data.get('address', '')}\n"
        f"📞 Telefon: {message.text}\n\n"
        f"Tez orada admin siz bilan bog'lanadi!",
        reply_markup=main_menu_kb(),
        parse_mode="HTML",
    )

    # Adminga xabar yuborish
    from bot.config import ADMIN_IDS
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                admin_id,
                f"🆕 <b>Yangi buyurtma!</b>\n\n"
                f"👤 {message.from_user.full_name} (@{message.from_user.username or 'yo\'q'})\n"
                f"🆔 #{order_id[-6:]}\n"
                f"💰 {total:,} {CURRENCY}\n"
                f"📍 {data.get('address', '')}\n"
                f"📞 {message.text}",
                parse_mode="HTML",
            )
        except Exception:
            pass

    await state.clear()


# ─── User Orders ─────────────────────────────────────────

@router.message(F.text == "📋 Buyurtmalarim")
async def show_user_orders(message: Message):
    orders = db.get_user_orders(message.from_user.id)
    if not orders:
        await message.answer("📋 Sizda hali buyurtmalar yo'q.")
        return
    await message.answer("📋 <b>Buyurtmalaringiz:</b>", reply_markup=user_orders_kb(message.from_user.id), parse_mode="HTML")


@router.callback_query(F.data.startswith("order:"))
async def show_order_detail(callback: CallbackQuery):
    oid = callback.data.split(":", 1)[1]
    order = db.get_order(oid)
    if not order:
        await callback.answer("Buyurtma topilmadi!", show_alert=True)
        return

    status_names = {
        "pending": "⏳ Kutilmoqda",
        "confirmed": "✅ Tasdiqlangan",
        "shipped": "🚚 Yetkazilmoqda",
        "delivered": "📦 Yetkazilgan",
        "cancelled": "❌ Bekor qilingan",
    }
    status = status_names.get(order.get("status", ""), "❓ Noma'lum")

    text = (
        f"📋 <b>Buyurtma #{oid[-6:]}</b>\n\n"
        f"👤 {order.get('full_name', '')}\n"
        f"📞 {order.get('phone', '')}\n"
        f"📍 {order.get('address', '')}\n\n"
        f"📦 <b>Mahsulotlar:</b>\n"
    )
    for pid, qty in order.get("items", {}).items():
        product = db.get_product(pid)
        if product:
            text += f"• {product['name']} x{qty}\n"
    text += f"\n💰 <b>Jami: {order.get('total', 0):,} {CURRENCY}</b>\n"
    text += f"\n📊 Holat: {status}"
    await callback.message.edit_text(text, reply_markup=user_orders_kb(callback.from_user.id), parse_mode="HTML")


# ─── Info ────────────────────────────────────────────────

@router.message(F.text == "ℹ️ Ma'lumot")
async def show_info(message: Message):
    products = db.get_products()
    users = db.get_users()
    orders = db.get_orders()
    await message.answer(
        f"ℹ️ <b>Online Do'kon Haqida</b>\n\n"
        f"📦 Mahsulotlar: {len(products)} ta\n"
        f"👥 Foydalanuvchilar: {len(users)} ta\n"
        f"📋 Buyurtmalar: {len(orders)} ta\n\n"
        f"📞 Savol-javob uchun admin bilan bog'laning.",
        parse_mode="HTML",
    )
