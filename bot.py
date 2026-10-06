import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, ADMIN_IDS
from database import db
from handlers import admin_router, user_router

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Botni ishga tushiruvchi asosiy funksiya"""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "\n" + "=" * 60 + "\n"
            "❌ XATOLIK: BOT_TOKEN ko'rsatilmadi!\n"
            "Iltimos, '.env' faylini oching va Telegram @BotFather dan olingan tokenni kiriting.\n"
            "Masalan: BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRstuVWXyz\n"
            "=" * 60
        )
        sys.exit(1)

    logger.info("Ma'lumotlar bazasi initsializatsiya qilinmoqda...")
    await db.init_db()

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Routerlarni ulash (Admin routerni birinchi ulash tavsiya etiladi)
    dp.include_router(admin_router)
    dp.include_router(user_router)

    # Eski kutilib qolgan xabarlarni o'chirish
    await bot.delete_webhook(drop_pending_updates=True)

    bot_info = await bot.get_me()
    logger.info(f"✅ Bot muvaffaqiyatli ishga tushdi: @{bot_info.username}")
    logger.info(f"👑 Admin ID lar: {ADMIN_IDS}")

    # Adminlarga bot yoqilgani haqida xabar berish
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=f"🟢 <b>Bot muvaffaqiyatli ishga tushdi!</b>\n🤖 @{bot_info.username}",
                parse_mode="HTML"
            )
        except Exception:
            pass

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
