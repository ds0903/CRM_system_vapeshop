import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from configuration.settings import settings
from bot.routers import admin_cmd, registration
from database.session import AsyncSessionLocal


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Middleware для бази даних
    @dp.update.middleware()
    async def db_session_middleware(handler, event, data):
        async with AsyncSessionLocal() as session:
            data['session'] = session
            return await handler(event, data)
    
    dp.include_router(admin_cmd.router)
    dp.include_router(registration.router)
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
