import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from bot.utils.config import BOT_TOKEN
from bot.handlers import location, photo, video

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


async def main():
    """Main function to start the bot"""
    # Initialize bot with default properties
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Initialize dispatcher
    dp = Dispatcher()
    
    # Register routers
    dp.include_router(location.router)
    dp.include_router(photo.router)
    dp.include_router(video.router)
    
    # Delete webhook and start polling
    await bot.delete_webhook(drop_pending_updates=True)
    
    try:
        logging.info("Bot started")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())