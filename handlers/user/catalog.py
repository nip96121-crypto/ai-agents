from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from database import db
from keyboards import categories_keyboard, products_keyboard, product_detail_keyboard
from utils.helpers import format_currency

router = Router()


@router.message(F.text == "🛍 Mahsulotlar katalogi")
async def show_catalog_message(message: Message):
    """Katalog bo'limi - kategoriyalarni ko'rsatish"""
    categories = await db.get_categories()
    if not categories:
        await message.answer("⚠️ Hozircha mahsulot toifalari mavjud emas.")
        return

    text = "📁 <b>Mahsulot toifalari:</b>\n\nKerakli toifani tanlang:"
    await message.answer(text, parse_mode="HTML", reply_markup=categories_keyboard(categories))


@router.callback_query(F.data == "catalog")
async def show_catalog_callback(callback: CallbackQuery):
    """Inline tugma orqali katalogga qaytish"""
    await callback.answer()
    categories = await db.get_categories()
    if not categories:
        await callback.message.edit_text("⚠️ Hozircha mahsulot toifalari mavjud emas.")
        return

    text = "📁 <b>Mahsulot toifalari:</b>\n\nKerakli toifani tanlang:"
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=categories_keyboard(categories))
    except Exception:
        await callback.message.delete()
        await callback.message.answer(text, parse_mode="HTML", reply_markup=categories_keyboard(categories))


@router.callback_query(F.data.startswith("cat_"))
async def show_category_products(callback: CallbackQuery):
    """Kategoriya tanlanganda uning mahsulotlarini ko'rsatish"""
    await callback.answer()
    category_id = int(callback.data.split("_")[1])
    category = await db.get_category(category_id)
    products = await db.get_products_by_category(category_id)

    cat_name = category["name"] if category else "Toifa"

    if not products:
        await callback.message.edit_text(
            f"⚠️ <b>{cat_name}</b> toifasida hozircha mahsulotlar mavjud emas.",
            parse_mode="HTML",
            reply_markup=categories_keyboard(await db.get_categories())
        )
        return

    text = f"📂 <b>{cat_name}</b> toifasidagi mahsulotlar:\n\nBatafsil ma'lumot olish uchun mahsulotni tanlang:"
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=products_keyboard(category_id, products))
    except Exception:
        await callback.message.delete()
        await callback.message.answer(text, parse_mode="HTML", reply_markup=products_keyboard(category_id, products))


@router.callback_query(F.data.startswith("prod_"))
async def show_product_detail(callback: CallbackQuery):
    """Mahsulot kartasini ko'rsatish"""
    await callback.answer()
    product_id = int(callback.data.split("_")[1])
    product = await db.get_product(product_id)

    if not product:
        await callback.answer("❌ Mahsulot topilmadi!", show_alert=True)
        return

    caption = (
        f"🏷 <b>{product['name']}</b>\n\n"
        f"📝 <b>Tavsifi:</b>\n{product['description']}\n\n"
        f"💰 <b>Narxi:</b> {format_currency(product['price'])}\n"
    )

    markup = product_detail_keyboard(product_id=product["id"], category_id=product["category_id"], quantity=1)

    # Agar mahsulotda rasm bo'lsa
    if product.get("image"):
        try:
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=product["image"],
                caption=caption,
                parse_mode="HTML",
                reply_markup=markup
            )
            return
        except Exception:
            pass

    # Agar rasm bo'lmasa yoki yuborishda xatolik bo'lsa matn ko'rinishida chiqarish
    try:
        await callback.message.edit_text(caption, parse_mode="HTML", reply_markup=markup)
    except Exception:
        await callback.message.delete()
        await callback.message.answer(caption, parse_mode="HTML", reply_markup=markup)


@router.callback_query(F.data.startswith("qty_inc_"))
async def qty_increment(callback: CallbackQuery):
    """Mahsulot sonini oshirish"""
    parts = callback.data.split("_")
    product_id = int(parts[2])
    qty = int(parts[3]) + 1
    product = await db.get_product(product_id)
    if not product:
        await callback.answer()
        return

    await callback.answer()
    markup = product_detail_keyboard(product_id=product_id, category_id=product["category_id"], quantity=qty)
    try:
        await callback.message.edit_reply_markup(reply_markup=markup)
    except Exception:
        pass


@router.callback_query(F.data.startswith("qty_dec_"))
async def qty_decrement(callback: CallbackQuery):
    """Mahsulot sonini kamaytirish (kamida 1)"""
    parts = callback.data.split("_")
    product_id = int(parts[2])
    qty = max(1, int(parts[3]) - 1)
    product = await db.get_product(product_id)
    if not product:
        await callback.answer()
        return

    await callback.answer()
    markup = product_detail_keyboard(product_id=product_id, category_id=product["category_id"], quantity=qty)
    try:
        await callback.message.edit_reply_markup(reply_markup=markup)
    except Exception:
        pass


@router.callback_query(F.data.startswith("addcart_"))
async def add_to_cart_handler(callback: CallbackQuery):
    """Mahsulotni savatchaga qo'shish"""
    parts = callback.data.split("_")
    product_id = int(parts[1])
    quantity = int(parts[2])
    user_id = callback.from_user.id

    product = await db.get_product(product_id)
    if not product:
        await callback.answer("❌ Mahsulot topilmadi!", show_alert=True)
        return

    await db.add_to_cart(user_id=user_id, product_id=product_id, quantity=quantity)
    await callback.answer(
        f"✅ {product['name']} ({quantity} dona) savatchaga qo'shildi!",
        show_alert=True
    )


@router.callback_query(F.data == "noop")
async def noop_handler(callback: CallbackQuery):
    """Bosilganda hech narsa qilmaydigan informatsion tugmalar"""
    await callback.answer()
