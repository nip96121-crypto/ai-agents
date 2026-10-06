import aiosqlite
from typing import List, Dict, Any, Optional
from config import DB_PATH


class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    async def init_db(self):
        """Ma'lumotlar bazasi jadvallarini yaratish va boshlang'ich ma'lumotlarni kiritish"""
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("PRAGMA foreign_keys = ON;")

            # Foydalanuvchilar jadvali
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    username TEXT,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Kategoriyalar jadvali
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                );
            """)

            # Mahsulotlar jadvali
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    image TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Savatcha jadvali
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS cart (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                    quantity INTEGER NOT NULL DEFAULT 1,
                    UNIQUE(user_id, product_id)
                );
            """)

            # Buyurtmalar jadvali
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    total_price REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    customer_name TEXT NOT NULL,
                    customer_phone TEXT NOT NULL,
                    address TEXT,
                    latitude REAL,
                    longitude REAL,
                    payment_method TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Buyurtma mahsulotlari jadvali
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                    product_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL
                );
            """)

            await conn.commit()

            # Namunaviy ma'lumotlar kiritish (agar kategoriya bo'lmasa)
            cursor = await conn.execute("SELECT COUNT(*) FROM categories;")
            count = (await cursor.fetchone())[0]
            if count == 0:
                await conn.execute("INSERT INTO categories (name) VALUES ('📱 Smartfonlar');")
                await conn.execute("INSERT INTO categories (name) VALUES ('💻 Noutbuklar');")
                await conn.execute("INSERT INTO categories (name) VALUES ('🎧 Aksessuarlar');")
                await conn.commit()

                # Namunaviy mahsulotlar
                await conn.execute("""
                    INSERT INTO products (category_id, name, description, price, image)
                    VALUES (1, 'iPhone 15 Pro 128GB', 'Super Retina XDR ekran, A17 Pro chip, titan korpus.', 13500000, '');
                """)
                await conn.execute("""
                    INSERT INTO products (category_id, name, description, price, image)
                    VALUES (1, 'Samsung Galaxy S24 Ultra', 'Dynamic AMOLED 2X, Snapdragon 8 Gen 3, S-Pen.', 14200000, '');
                """)
                await conn.execute("""
                    INSERT INTO products (category_id, name, description, price, image)
                    VALUES (2, 'MacBook Air M2 13.6"', 'Apple M2 chip, 8GB RAM, 256GB SSD, Liquid Retina.', 12500000, '');
                """)
                await conn.execute("""
                    INSERT INTO products (category_id, name, description, price, image)
                    VALUES (3, 'AirPods Pro 2', 'Faol shovqinni to''xtatish (ANC), MagSafe zaryadka.', 2700000, '');
                """)
                await conn.commit()

    # --- Foydalanuvchilar ---
    async def add_or_update_user(self, user_id: int, full_name: str, username: Optional[str] = None, phone: Optional[str] = None):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("""
                INSERT INTO users (user_id, full_name, username, phone)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    full_name = excluded.full_name,
                    username = COALESCE(excluded.username, users.username),
                    phone = COALESCE(excluded.phone, users.phone);
            """, (user_id, full_name, username, phone))
            await conn.commit()

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("SELECT * FROM users WHERE user_id = ?;", (user_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def update_user_phone(self, user_id: int, phone: str):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("UPDATE users SET phone = ? WHERE user_id = ?;", (phone, user_id))
            await conn.commit()

    async def get_all_user_ids(self) -> List[int]:
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute("SELECT user_id FROM users;")
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def get_users_count(self) -> int:
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute("SELECT COUNT(*) FROM users;")
            row = await cursor.fetchone()
            return row[0] if row else 0

    # --- Kategoriyalar ---
    async def get_categories(self) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("SELECT * FROM categories ORDER BY id ASC;")
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def get_category(self, category_id: int) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("SELECT * FROM categories WHERE id = ?;", (category_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def add_category(self, name: str) -> int:
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute("INSERT INTO categories (name) VALUES (?);", (name.strip(),))
            await conn.commit()
            return cursor.lastrowid

    async def delete_category(self, category_id: int):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("PRAGMA foreign_keys = ON;")
            await conn.execute("DELETE FROM categories WHERE id = ?;", (category_id,))
            await conn.commit()

    # --- Mahsulotlar ---
    async def get_products_by_category(self, category_id: int) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                "SELECT * FROM products WHERE category_id = ? AND is_active = 1 ORDER BY id DESC;",
                (category_id,)
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                "SELECT p.*, c.name as category_name FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE p.id = ?;",
                (product_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def add_product(self, category_id: int, name: str, description: str, price: float, image: str = "") -> int:
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(
                "INSERT INTO products (category_id, name, description, price, image) VALUES (?, ?, ?, ?, ?);",
                (category_id, name.strip(), description.strip(), price, image.strip())
            )
            await conn.commit()
            return cursor.lastrowid

    async def delete_product(self, product_id: int):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("PRAGMA foreign_keys = ON;")
            await conn.execute("DELETE FROM products WHERE id = ?;", (product_id,))
            await conn.commit()

    async def get_products_count(self) -> int:
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute("SELECT COUNT(*) FROM products WHERE is_active = 1;")
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def search_products(self, query: str) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            pattern = f"%{query.strip()}%"
            cursor = await conn.execute(
                "SELECT * FROM products WHERE is_active = 1 AND (name LIKE ? OR description LIKE ?) LIMIT 10;",
                (pattern, pattern)
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    # --- Savatcha (Cart) ---
    async def get_cart(self, user_id: int) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("""
                SELECT c.id as cart_id, c.quantity, p.id as product_id, p.name, p.price, p.image,
                       (c.quantity * p.price) as subtotal
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id = ?
                ORDER BY c.id ASC;
            """, (user_id,))
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def add_to_cart(self, user_id: int, product_id: int, quantity: int = 1):
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute(
                "SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?;",
                (user_id, product_id)
            )
            row = await cursor.fetchone()
            if row:
                new_qty = row[0] + quantity
                await conn.execute(
                    "UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?;",
                    (new_qty, user_id, product_id)
                )
            else:
                await conn.execute(
                    "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?);",
                    (user_id, product_id, quantity)
                )
            await conn.commit()

    async def update_cart_quantity(self, user_id: int, product_id: int, quantity: int):
        async with aiosqlite.connect(self.db_path) as conn:
            if quantity <= 0:
                await conn.execute(
                    "DELETE FROM cart WHERE user_id = ? AND product_id = ?;",
                    (user_id, product_id)
                )
            else:
                await conn.execute(
                    "UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?;",
                    (quantity, user_id, product_id)
                )
            await conn.commit()

    async def remove_from_cart(self, user_id: int, product_id: int):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute(
                "DELETE FROM cart WHERE user_id = ? AND product_id = ?;",
                (user_id, product_id)
            )
            await conn.commit()

    async def clear_cart(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("DELETE FROM cart WHERE user_id = ?;", (user_id,))
            await conn.commit()

    # --- Buyurtmalar (Orders) ---
    async def create_order(
        self,
        user_id: int,
        total_price: float,
        customer_name: str,
        customer_phone: str,
        address: str = "",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        payment_method: str = "Naqd pul",
        items: Optional[List[Dict[str, Any]]] = None
    ) -> int:
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute("""
                INSERT INTO orders (user_id, total_price, status, customer_name, customer_phone, address, latitude, longitude, payment_method)
                VALUES (?, ?, 'pending', ?, ?, ?, ?, ?, ?);
            """, (user_id, total_price, customer_name, customer_phone, address, latitude, longitude, payment_method))
            order_id = cursor.lastrowid

            if items:
                for item in items:
                    await conn.execute("""
                        INSERT INTO order_items (order_id, product_id, product_name, price, quantity)
                        VALUES (?, ?, ?, ?, ?);
                    """, (order_id, item["product_id"], item["name"], item["price"], item["quantity"]))

            # Savatchani tozalash
            await conn.execute("DELETE FROM cart WHERE user_id = ?;", (user_id,))
            await conn.commit()
            return order_id

    async def get_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("SELECT * FROM orders WHERE id = ?;", (order_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_order_items(self, order_id: int) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("SELECT * FROM order_items WHERE order_id = ?;", (order_id,))
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def get_user_orders(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT ?;",
                (user_id, limit)
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def get_orders(self, status: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            if status:
                cursor = await conn.execute(
                    "SELECT * FROM orders WHERE status = ? ORDER BY id DESC LIMIT ?;",
                    (status, limit)
                )
            else:
                cursor = await conn.execute(
                    "SELECT * FROM orders ORDER BY id DESC LIMIT ?;",
                    (limit,)
                )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def update_order_status(self, order_id: int, status: str):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("UPDATE orders SET status = ? WHERE id = ?;", (status, order_id))
            await conn.commit()

    async def get_statistics(self) -> Dict[str, Any]:
        async with aiosqlite.connect(self.db_path) as conn:
            # Foydalanuvchilar soni
            cursor = await conn.execute("SELECT COUNT(*) FROM users;")
            users_count = (await cursor.fetchone())[0]

            # Jami mahsulotlar
            cursor = await conn.execute("SELECT COUNT(*) FROM products WHERE is_active = 1;")
            products_count = (await cursor.fetchone())[0]

            # Jami buyurtmalar
            cursor = await conn.execute("SELECT COUNT(*) FROM orders;")
            orders_count = (await cursor.fetchone())[0]

            # Kutilayotgan buyurtmalar
            cursor = await conn.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending';")
            pending_orders = (await cursor.fetchone())[0]

            # Yakunlangan buyurtmalar va umumiy tushum
            cursor = await conn.execute("SELECT COALESCE(SUM(total_price), 0) FROM orders WHERE status = 'completed';")
            total_revenue = (await cursor.fetchone())[0]

            return {
                "users_count": users_count,
                "products_count": products_count,
                "orders_count": orders_count,
                "pending_orders": pending_orders,
                "total_revenue": total_revenue
            }
