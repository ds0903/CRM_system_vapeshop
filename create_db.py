import asyncio
from database.base import Base
from database.session import engine
from entities.models import Admin, City, Product, User, RegistrationRequest, Order  # Імпортуємо моделі!


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблиці створено успішно!")


if __name__ == "__main__":
    asyncio.run(create_tables())
