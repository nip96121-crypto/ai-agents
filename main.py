import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import BOT_TOKEN
from bot.database import init_default_data
from bot.handlers.user import router as user_router
from bot.handlers.admin import router as admin_router


async def main():
    # Logging sozlash
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Token tekshirish
    if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_TOKEN_HERE":
        print("❌ XATO: BOT_TOKEN kiritilmagan!")
        print("   .env faylini oching va BOT_TOKEN ni kiriting.")
        print("   Token olish uchun @BotFather ga /newbot yuboring.")
        return

    # Bot yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Dispatcher yaratish
    dp = Dispatcher()

    # Routerlarni qo'shish
    dp.include_router(admin_router)
    dp.include_router(user_router)

    # Standart ma'lumotlarni yaratish
    init_default_data()

    print("🤖 Bot ishga tushdi!")
    print("📌 /admin — Admin panel")
    print("📌 /start — Bosh menyu")

    # Polling boshlash
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
