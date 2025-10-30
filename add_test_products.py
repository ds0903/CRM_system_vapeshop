import asyncio
from database.session import AsyncSessionLocal
from entities.models import Product, City
from sqlalchemy import select


async def add_test_products():
    async with AsyncSessionLocal() as session:
        # Отримуємо Dresden
        result = await session.execute(
            select(City).where(City.name == "Dresden")
        )
        dresden = result.scalar_one_or_none()
        
        if not dresden:
            print("❌ Місто Dresden не знайдено. Спочатку запусти add_cities.py")
            return
        
        # Тестові товари
        products = [
            Product(
                code="003",
                name="Elfliq",
                flavor="Grape",
                purchase_price=4.0,
                purchase_quantity=10,
                sale_price=10.0,
                sold_quantity=2,
                avg_sale_price=10.0,
                stock=8,
                city_id=dresden.id
            ),
            Product(
                code="005",
                name="Elfliq",
                flavor="Strawberry",
                purchase_price=4.0,
                purchase_quantity=15,
                sale_price=10.0,
                sold_quantity=5,
                avg_sale_price=10.0,
                stock=10,
                city_id=dresden.id
            ),
            Product(
                code="007",
                name="Lost Mary",
                flavor="Blueberry",
                purchase_price=5.0,
                purchase_quantity=20,
                sale_price=12.0,
                sold_quantity=8,
                avg_sale_price=12.0,
                stock=12,
                city_id=dresden.id
            ),
        ]
        
        for product in products:
            session.add(product)
            print(f"✅ Додано товар: {product.code} - {product.name} {product.flavor}")
        
        await session.commit()
        print("\n✅ Тестові товари успішно додано!")


if __name__ == "__main__":
    asyncio.run(add_test_products())
