import asyncio
from database.session import AsyncSessionLocal
from entities.models import City


async def add_cities():
    async with AsyncSessionLocal() as session:
        # Перевіряємо чи є вже міста
        cities_to_add = ["Dresden", "Munchen", "Berlin", "Hamburg"]
        
        for city_name in cities_to_add:
            # Перевіряємо чи існує місто
            from sqlalchemy import select
            result = await session.execute(
                select(City).where(City.name == city_name)
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                city = City(name=city_name, is_active=True)
                session.add(city)
                print(f"✅ Додано місто: {city_name}")
            else:
                print(f"ℹ️ Місто {city_name} вже існує")
        
        await session.commit()
        print("\n✅ Міста успішно додано!")


if __name__ == "__main__":
    asyncio.run(add_cities())
