import json
import os
from typing import Any
from bot.config import DATA_DIR, USERS_FILE, PRODUCTS_FILE, CATEGORIES_FILE, CARTS_FILE, ORDERS_FILE


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load(file_path: str) -> dict:
    _ensure_data_dir()
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(file_path: str, data: dict):
    _ensure_data_dir()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─── Users ───────────────────────────────────────────────

def get_users() -> dict:
    return _load(USERS_FILE)


def get_user(user_id: int) -> dict | None:
    return get_users().get(str(user_id))


def save_user(user_id: int, data: dict):
    users = get_users()
    users[str(user_id)] = data
    _save(USERS_FILE, users)


def update_user(user_id: int, **kwargs):
    users = get_users()
    uid = str(user_id)
    if uid in users:
        users[uid].update(kwargs)
        _save(USERS_FILE, users)


# ─── Categories ──────────────────────────────────────────

def get_categories() -> dict:
    return _load(CATEGORIES_FILE)


def save_categories(categories: dict):
    _save(CATEGORIES_FILE, categories)


def add_category(cat_id: str, name: str):
    cats = get_categories()
    cats[cat_id] = {"name": name}
    save_categories(cats)


def delete_category(cat_id: str):
    cats = get_categories()
    cats.pop(cat_id, None)
    save_categories(cats)


# ─── Products ────────────────────────────────────────────

def get_products() -> dict:
    return _load(PRODUCTS_FILE)


def get_product(product_id: str) -> dict | None:
    return get_products().get(product_id)


def save_products(products: dict):
    _save(PRODUCTS_FILE, products)


def add_product(product_id: str, data: dict):
    products = get_products()
    products[product_id] = data
    save_products(products)


def delete_product(product_id: str):
    products = get_products()
    products.pop(product_id, None)
    save_products(products)


def update_product(product_id: str, **kwargs):
    products = get_products()
    if product_id in products:
        products[product_id].update(kwargs)
        save_products(products)


# ─── Carts ───────────────────────────────────────────────

def get_carts() -> dict:
    return _load(CARTS_FILE)


def get_cart(user_id: int) -> dict:
    carts = get_carts()
    return carts.get(str(user_id), {})


def save_cart(user_id: int, cart: dict):
    carts = get_carts()
    carts[str(user_id)] = cart
    _save(CARTS_FILE, carts)


def add_to_cart(user_id: int, product_id: str, qty: int = 1):
    cart = get_cart(user_id)
    if product_id in cart:
        cart[product_id] += qty
    else:
        cart[product_id] = qty
    save_cart(user_id, cart)


def remove_from_cart(user_id: int, product_id: str):
    cart = get_cart(user_id)
    cart.pop(product_id, None)
    save_cart(user_id, cart)


def clear_cart(user_id: int):
    save_cart(user_id, {})


# ─── Orders ──────────────────────────────────────────────

def get_orders() -> dict:
    return _load(ORDERS_FILE)


def get_order(order_id: str) -> dict | None:
    return get_orders().get(order_id)


def get_user_orders(user_id: int) -> dict:
    return {k: v for k, v in get_orders().items() if v.get("user_id") == user_id}


def save_order(order_id: str, data: dict):
    orders = get_orders()
    orders[order_id] = data
    _save(ORDERS_FILE, orders)


def update_order(order_id: str, **kwargs):
    orders = get_orders()
    if order_id in orders:
        orders[order_id].update(kwargs)
        _save(ORDERS_FILE, orders)


# ─── Init default data ──────────────────────────────────

def init_default_data():
    """Agar kategoriyalar bo'sh bo'lsa, standart kategoriyalarni qo'shadi"""
    cats = get_categories()
    if not cats:
        default_cats = {
            "electronics": {"name": "📱 Elektronika"},
            "clothing": {"name": "👕 Kiyim-kechak"},
            "food": {"name": "🍔 Oziq-ovqat"},
            "books": {"name": "📚 Kitoblar"},
            "home": {"name": "🏠 Uy buyumlari"},
        }
        save_categories(default_cats)
