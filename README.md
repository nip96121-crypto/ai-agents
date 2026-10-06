# 🛍 Telegram Onlayn Magazin Boti (Admin Panel Bilan)

Zamonaviy, tezkor va qulay Telegram onlayn do'kon boti. Bot **Python 3**, **aiogram 3** va asinxron **SQLite (aiosqlite)** bazasida yaratilgan.

---

## 🌟 Botning Asosiy Imkoniyatlari

### 👤 1. Foydalanuvchilar (Xaridorlar) uchun:
* 🛍 **Mahsulotlar katalogi**: Toifalar (kategoriyalar) va mahsulotlarni qulay inline tugmalar orqali ko'rish.
* 📦 **Mahsulot kartochkasi**: Nomi, tavsifi, narxi, rasmi va sonini tanlash (+/-).
* 🛒 **Interaktiv savatcha**: Mahsulotlar sonini oshirish/kamaytirish, bittalab o'chirish yoki savatni tozalash, jami summani hisoblash.
* 📝 **Tezkor buyurtma berish**:
  - Ism-familiya kiritish;
  - Telefon raqamni bitta tugma orqali yuborish (`request_contact`);
  - Joylashuv (geolokatsiya) yoki matnli manzil yuborish;
  - To'lov turini tanlash (Naqd pul / Plastik karta / Click / Payme);
  - Buyurtmani tasdiqlash.
* 📦 **Buyurtmalar tarixi**: «📦 Buyurtmalarim» bo'limida avvalgi buyurtmalar ro'yxati va ularning holatini kuzatish.
* 🔍 **Mahsulot qidiruv**: Do'kondan qidirilayotgan mahsulotni nomi bo'yicha bir zumda topish.
* ℹ️ **Do'kon haqida va Aloqa**: Aloqa ma'lumotlari va qo'llab-quvvatlash xizmati.

---

### 👑 2. Admin Panel (Boshqaruv Paneli):
Adminlar uchun alohida menyu (`/admin` buyrug'i yoki «🔐 Admin Panel» tugmasi faqat `ADMIN_IDS` ro'yxatidagi foydalanuvchilarga ko'rinadi).

* 📊 **Do'kon statistikasi**:
  - Foydalanuvchilar soni;
  - Faol mahsulotlar soni;
  - Jami buyurtmalar soni;
  - Yangi kutilayotgan buyurtmalar;
  - Umumiy amalga oshirilgan savdo summasi.
* 🗂 **Toifalar (Kategoriyalar) boshqaruvi**:
  - Yangi toifa qo'shish;
  - Keraksiz toifani o'chirish (toifaga tegishli mahsulotlar bilan birga).
* 🛍 **Mahsulotlar boshqaruvi**:
  - Istalgan toifaga yangi mahsulot qo'shish (nomi, tavsifi, narxi va rasmi);
  - Mahsulotlarni toifalar bo'yicha ko'rish va o'chirish.
* 📋 **Buyurtmalar boshqaruvi**:
  - Yangi tushgan buyurtmalar haqida adminlarga darhol bildirishnoma (notification) borishi;
  - Mijoz yuborgan lokatsiya (xarita) va telefon raqamini ko'rish;
  - Buyurtma holatini bitta tugma bilan o'zgartirish:
    - ✅ **Tasdiqlash** (Tayyorlanmoqda)
    - 🚚 **Yetkazilmoqda**
    - 🏁 **Yakunlash** (Yetkazildi)
    - ❌ **Bekor qilish**
  - 🔔 **Avtomatik mijozga bildirishnoma**: Admin buyurtma holatini o'zgartirganda mijozga darhol bot nomidan xabar boradi!
* 📢 **Ommaviy xabar tarqatish (Rassilka)**:
  - Botning barcha foydalanuvchilariga reklama, yangiliklar yoki chegirmalar haqida xabar (matn yoki rasmli xabar) jo'natish.

---

## 🚀 Botni Ishga Tushirish Bo'yicha Qo'llanma

### 1-qadam: Bot Token olish
1. Telegramda [@BotFather](https://t.me/botfather) botiga kiring.
2. `/newbot` buyrug'ini yuboring va ko'rsatmalarga asosan botingizga nom va username bering.
3. BotFather sizga bergan **API Tokenni** nusxalab (kopiya qilib) oling.

### 2-qadam: Admin Telegram ID raqamini aniqlash
1. Telegramda [@userinfobot](https://t.me/userinfobot) yoki [@myidbot](https://t.me/myidbot) botiga kiring va `/start` bosing.
2. Bot sizga `Id: 123456789` kabi raqamli ID beradi.

### 3-qadam: `.env` faylini to'ldirish
Loyihaning asosiy papkasidagi `.env` faylini oching va ma'lumotlarni kiriting:

```env
BOT_TOKEN=1234567890:AAH... (BotFather bergan token)
ADMIN_IDS=123456789 (O'zingizning Telegram ID raqamingiz)
DB_PATH=shop.db
```

*(Agar adminlar bir nechta bo'lsa, ularning ID raqamlarini vergul bilan ajratib yozing: `ADMIN_IDS=123456789,987654321`)*

---

### 4-qadam: Kutubxonalarni o'rnatish
Agar kutubxonalar o'rnatilmagan bo'lsa:
```bash
pip install -r requirements.txt
```

### 5-qadam: Botni ishga tushirish
Terminal yoki buyruqlar satrida quyidagilardan birini bering:

```bash
npm run dev
```
*(yoki `python bot.py`)*

Konsolda quyidagi xabarni ko'rasiz:
```text
✅ Bot muvaffaqiyatli ishga tushdi: @Shop_Ayubxon_bot
👑 Admin ID lar: [8604180055]
```

Endi Telegramda o'z botingizga kirib `/start` tugmasini bosing! 🎉

---

## 📁 Loyiha Tuzilishi

```
shop bot/
├── .env                  # Maxfiy sozlamalar (Bot token, Admin ID)
├── .env.example          # Namuna sozlamalar
├── config.py             # Sozlamalarni o'quvchi konfiguratsiya moduli
├── bot.py                # Botni ishga tushirish fayli (Asosiy)
├── requirements.txt      # Kerakli Python kutubxonalari
├── shop.db               # SQLite ma'lumotlar bazasi (avtomatik yaratiladi)
├── database/             # Ma'lumotlar bazasi qismi
│   ├── __init__.py
│   └── db.py             # Barcha asinxron SQL amallari (foydalanuvchilar, toifalar, mahsulotlar, savat, buyurtmalar)
├── handlers/             # Telegram xabar va buyruqlarini qabul qiluvchilar
│   ├── __init__.py
│   ├── user/             # Foydalanuvchi bo'limlari
│   │   ├── start.py      # /start va umumiy ma'lumotlar
│   │   ├── catalog.py    # Toifalar va mahsulotlarni ko'rish, savatga qo'shish
│   │   ├── cart.py       # Savatchani boshqarish (+/-, o'chirish)
│   │   ├── order.py      # Buyurtma rasmiylashtirish va adminlarga xabar yuborish
│   │   ├── my_orders.py  # Buyurtmalar tarixi
│   │   └── search.py     # Mahsulot qidirish
│   └── admin/            # Admin boshqaruv paneli
│       ├── admin_main.py # /admin bosh menyusi va statistika
│       ├── categories.py # Yangi toifa qo'shish va o'chirish
│       ├── products.py   # Yangi mahsulot qo'shish va o'chirish
│       ├── orders.py     # Buyurtmalarni boshqarish va mijozga bildirishnomalar
│       └── broadcast.py  # Foydalanuvchilarga ommaviy xabar tarqatish
├── keyboards/            # Tugmalar klaviaturasi
│   ├── __init__.py
│   ├── default.py        # Asosiy menyu, telefon va lokatsiya tugmalari
│   └── inline.py         # Katalog, savatcha va admin inline tugmalari
├── states/               # FSM (Finite State Machine) holatlari
│   ├── __init__.py
│   ├── user_states.py    # Buyurtma berish va qidiruv holatlari
│   └── admin_states.py   # Mahsulot, toifa va reklama tarqatish holatlari
└── utils/                # Yordamchi vositalar
    ├── __init__.py
    └── helpers.py        # Narxni formatlash va holat matnlari
```
