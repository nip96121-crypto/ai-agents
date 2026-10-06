from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot import database as db
from bot.config import ADMIN_IDS, CURRENCY
from bot.keyboards import (
    admin_main_kb, admin_products_kb, admin_product_list_kb, admin_product_detail_kb,
    admin_categories_kb, admin_orders_kb, admin_order_detail_kb,
)

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


class AddProductState(StatesGroup):
    waiting_name = State()
    waiting_description = State()
    waiting_price = State()
    waiting_stock = State()
    waiting_category = State()


class AddCategoryState(StatesGroup):
    waiting_name = State()


# ─── Admin Panel Entry ───────────────────────────────────

@router.message(F.text == "/admin")
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Sizda admin huquqi yo'q!")
        return
    await message.answer(
        "🔧 <b>Admin Panel</b>\n\nBoshqarish uchun bo'limni tanlang:",
        reply_markup=admin_main_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.edit_text(
        "🔧 <b>Admin Panel</b>\n\nBoshqarish uchun bo'limni tanlang:",
        reply_markup=admin_main_kb(),
        parse_mode="HTML",
    )


# ─── Statistics ──────────────────────────────────────────

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    products = db.get_products()
    users = db.get_users()
    orders = db.get_orders()
    total_revenue = sum(o.get("total", 0) for o in orders.values())
    pending_orders = sum(1 for o in orders.values() if o.get("status") == "pending")

    await callback.message.edit_text(
        f"📊 <b>Statistika</b>\n\n"
        f"📦 Mahsulotlar: {len(products)} ta\n"
        f"📂 Kategoriyalar: {len(db.get_categories())} ta\n"
        f"👥 Foydalanuvchilar: {len(users)} ta\n"
        f"📋 Jami buyurtmalar: {len(orders)} ta\n"
        f"⏳ Kutilayotgan: {pending_orders} ta\n"
        f"💰 Jami tushum: {total_revenue:,} {CURRENCY}",
        reply_markup=admin_main_kb(),
        parse_mode="HTML",
    )


# ─── Products Management ─────────────────────────────────

@router.callback_query(F.data == "admin_products")
async def admin_products(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.edit_text(
        "📦 <b>Mahsulotlar boshqaruvi</b>",
        reply_markup=admin_products_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "admin_list_products")
async def admin_list_products(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    products = db.get_products()
    if not products:
        await callback.message.edit_text(
            "📦 Mahsulotlar yo'q.\n\nYangi mahsulot qo'shing!",
            reply_markup=admin_products_kb(),
        )
        return
    await callback.message.edit_text(
        f"📦 <b>Mahsulotlar ({len(products)} ta):</b>",
        reply_markup=admin_product_list_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("admin_prod:"))
async def admin_product_detail(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    pid = callback.data.split(":")[1]
    product = db.get_product(pid)
    if not product:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return
    cats = db.get_categories()
    cat_name = cats.get(product.get("category", ""), {}).get("name", "Noma'lum")
    text = (
        f"🏷️ <b>{product['name']}</b>\n\n"
        f"📝 {product.get('description', 'Tavsif yo\'q')}\n\n"
        f"📂 Kategoriya: {cat_name}\n"
        f"💰 Narxi: {product['price']:,} {CURRENCY}\n"
        f"📦 Mavjud: {product.get('stock', 0)} dona"
    )
    await callback.message.edit_text(text, reply_markup=admin_product_detail_kb(pid), parse_mode="HTML")


# ─── Add Product ─────────────────────────────────────────

@router.callback_query(F.data == "admin_add_product")
async def admin_add_product(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("➕ <b>Yangi mahsulot qo'shish</b>\n\n📝 Mahsulot nomini kiriting:", parse_mode="HTML")
    await state.set_state(AddProductState.waiting_name)


@router.message(AddProductState.waiting_name)
async def add_product_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(name=message.text)
    await message.answer("📝 Tavsifini kiriting:")
    await state.set_state(AddProductState.waiting_description)


@router.message(AddProductState.waiting_description)
async def add_product_desc(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(description=message.text)
    await message.answer("💰 Narxini kiriting (faqat son):")
    await state.set_state(AddProductState.waiting_price)


@router.message(AddProductState.waiting_price)
async def add_product_price(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        price = int(message.text.replace(" ", "").replace(",", ""))
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat son kiriting:")
        return
    await state.update_data(price=price)
    await message.answer("📦 Mavjud miqdorini kiriting (son):")
    await state.set_state(AddProductState.waiting_stock)


@router.message(AddProductState.waiting_stock)
async def add_product_stock(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        stock = int(message.text)
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat son kiriting:")
        return
    await state.update_data(stock=stock)

    cats = db.get_categories()
    if not cats:
        await message.answer("❌ Kategoriyalar mavjud emas! Avval kategoriya qo'shing.")
        await state.clear()
        return

    buttons_text = "\n".join([f"  /{cid} — {cdata['name']}" for cid, cdata in cats.items()])
    await message.answer(
        f"📂 Kategoriyani tanlang:\n\n{buttons_text}\n\nKategoriya ID ni kiriting:"
    )
    await state.set_state(AddProductState.waiting_category)


@router.message(AddProductState.waiting_category)
async def add_product_category(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    cat_id = message.text.strip().replace("/", "")
    cats = db.get_categories()
    if cat_id not in cats:
        await message.answer("❌ Kategoriya topilmadi! Qaytadan kiriting:")
        return

    data = await state.get_data()
    product_id = f"prod_{message.date.timestamp():.0f}"

    db.add_product(product_id, {
        "name": data["name"],
        "description": data["description"],
        "price": data["price"],
        "stock": data["stock"],
        "category": cat_id,
    })

    await message.answer(
        f"✅ <b>Mahsulot qo'shildi!</b>\n\n"
        f"🏷️ {data['name']}\n"
        f"💰 {data['price']:,} {CURRENCY}\n"
        f"📦 {data['stock']} dona",
        reply_markup=admin_products_kb(),
        parse_mode="HTML",
    )
    await state.clear()


# ─── Delete Product ──────────────────────────────────────

@router.callback_query(F.data.startswith("admin_del_prod:"))
async def admin_delete_product(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    pid = callback.data.split(":")[1]
    product = db.get_product(pid)
    if product:
        db.delete_product(pid)
        await callback.answer(f"🗑️ {product['name']} o'chirildi!", show_alert=True)
    await callback.message.edit_text(
        "📦 <b>Mahsulotlar boshqaruvi</b>",
        reply_markup=admin_products_kb(),
        parse_mode="HTML",
    )


# ─── Categories Management ───────────────────────────────

@router.callback_query(F.data == "admin_categories")
async def admin_categories(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.edit_text(
        "📂 <b>Kategoriyalar boshqaruvi</b>",
        reply_markup=admin_categories_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "admin_add_category")
async def admin_add_category(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.edit_text("➕ <b>Yangi kategoriya</b>\n\n📝 Kategoriya nomini kiriting:", parse_mode="HTML")
    await state.set_state(AddCategoryState.waiting_name)


@router.message(AddCategoryState.waiting_name)
async def add_category_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    cat_id = f"cat_{message.date.timestamp():.0f}"
    db.add_category(cat_id, message.text)
    await message.answer(
        f"✅ Kategoriya qo'shildi: <b>{message.text}</b>",
        reply_markup=admin_categories_kb(),
        parse_mode="HTML",
    )
    await state.clear()


@router.callback_query(F.data.startswith("admin_del_cat:"))
async def admin_delete_category(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    cat_id = callback.data.split(":")[1]
    cats = db.get_categories()
    cat_name = cats.get(cat_id, {}).get("name", "")
    db.delete_category(cat_id)
    await callback.answer(f"🗑️ '{cat_name}' o'chirildi!", show_alert=True)
    await callback.message.edit_text(
        "📂 <b>Kategoriyalar boshqaruvi</b>",
        reply_markup=admin_categories_kb(),
        parse_mode="HTML",
    )


# ─── Orders Management ───────────────────────────────────

@router.callback_query(F.data == "admin_orders")
async def admin_orders(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    orders = db.get_orders()
    if not orders:
        await callback.message.edit_text(
            "📋 Buyurtmalar yo'q.",
            reply_markup=admin_main_kb(),
        )
        return
    await callback.message.edit_text(
        f"📋 <b>Buyurtmalar ({len(orders)} ta):</b>",
        reply_markup=admin_orders_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("admin_order:"))
async def admin_order_detail(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
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
        f"👤 {order.get('full_name', '')} (@{order.get('username', '')})\n"
        f"📞 {order.get('phone', '')}\n"
        f"📍 {order.get('address', '')}\n\n"
        f"📦 <b>Mahsulotlar:</b>\n"
    )
    for pid, qty in order.get("items", {}).items():
        product = db.get_product(pid)
        if product:
            text += f"• {product['name']} x{qty} = {product['price'] * qty:,} {CURRENCY}\n"
    text += f"\n💰 <b>Jami: {order.get('total', 0):,} {CURRENCY}</b>\n"
    text += f"\n📊 Holat: {status}"
    await callback.message.edit_text(text, reply_markup=admin_order_detail_kb(oid), parse_mode="HTML")


@router.callback_query(F.data.startswith("admin_set_status:"))
async def admin_set_status(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    parts = callback.data.split(":")
    oid = parts[1]
    new_status = parts[2]
    db.update_order(oid, status=new_status)

    status_names = {
        "pending": "⏳ Kutilmoqda",
        "confirmed": "✅ Tasdiqlangan",
        "shipped": "🚚 Yetkazilmoqda",
        "delivered": "📦 Yetkazilgan",
        "cancelled": "❌ Bekor qilingan",
    }

    order = db.get_order(oid)
    if order:
        # Foydalanuvchiga xabar yuborish
        try:
            await callback.bot.send_message(
                order["user_id"],
                f"📋 Buyurtma #{oid[-6:]} holati o'zgardi:\n"
                f"Yangi holat: {status_names.get(new_status, new_status)}",
            )
        except Exception:
            pass

    await callback.answer(f"✅ Holat o'zgartirildi: {status_names.get(new_status, new_status)}", show_alert=True)

    # Sahifani yangilash
    if order:
        status = status_names.get(order.get("status", ""), "❓ Noma'lum")
        text = (
            f"📋 <b>Buyurtma #{oid[-6:]}</b>\n\n"
            f"👤 {order.get('full_name', '')} (@{order.get('username', '')})\n"
            f"📞 {order.get('phone', '')}\n"
            f"📍 {order.get('address', '')}\n\n"
            f"📦 <b>Mahsulotlar:</b>\n"
        )
        for pid, qty in order.get("items", {}).items():
            product = db.get_product(pid)
            if product:
                text += f"• {product['name']} x{qty} = {product['price'] * qty:,} {CURRENCY}\n"
        text += f"\n💰 <b>Jami: {order.get('total', 0):,} {CURRENCY}</b>\n"
        text += f"\n📊 Holat: {status}"
        await callback.message.edit_text(text, reply_markup=admin_order_detail_kb(oid), parse_mode="HTML")


# ─── Users Management ────────────────────────────────────

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    users = db.get_users()
    if not users:
        await callback.message.edit_text(
            "👥 Foydalanuvchilar yo'q.",
            reply_markup=admin_main_kb(),
        )
        return
    text = f"👥 <b>Foydalanuvchilar ({len(users)} ta):</b>\n\n"
    for uid, u in users.items():
        text += f"• ID: <code>{uid}</code> | {u.get('full_name', '')} (@{u.get('username', '')})\n"
    await callback.message.edit_text(text, reply_markup=admin_main_kb(), parse_mode="HTML")
