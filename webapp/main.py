from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database.session import AsyncSessionLocal
from bot.utils.security import verify_admin_token
from entities.models import RegistrationRequest, User, City, Product, Order
from pydantic import BaseModel
from datetime import datetime
import json

app = FastAPI(title="Vapeshop Admin")

templates = Jinja2Templates(directory="webapp/templates")
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

def require_admin(token: str) -> int:
    try:
        payload = verify_admin_token(token)
        return int(payload["tg_id"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    # Отримуємо всі заявки зі статусом pending
    result = await db.execute(
        select(RegistrationRequest)
        .where(RegistrationRequest.status == "pending")
        .order_by(RegistrationRequest.created_at.desc())
    )
    requests = result.scalars().all()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "token": token,
        "requests": requests,
        "page_title": "Заявки на реєстрацію",
        "active_page": "registration"
    })

@app.get("/cities", response_class=HTMLResponse)
async def cities(request: Request, token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    return templates.TemplateResponse("cities.html", {
        "request": request,
        "token": token,
        "page_title": "Города",
        "active_page": "cities"
    })

@app.get("/order-tips", response_class=HTMLResponse)
async def order_tips(request: Request, token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    return templates.TemplateResponse("order_tips.html", {
        "request": request,
        "token": token,
        "page_title": "Советы по заказам",
        "active_page": "order-tips"
    })

@app.get("/assign-order", response_class=HTMLResponse)
async def assign_order(request: Request, token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    return templates.TemplateResponse("assign_order.html", {
        "request": request,
        "token": token,
        "page_title": "Назначить заказ",
        "active_page": "assign-order"
    })

@app.get("/statements", response_class=HTMLResponse)
async def statements(request: Request, token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    return templates.TemplateResponse("statements.html", {
        "request": request,
        "token": token,
        "page_title": "Выписки",
        "active_page": "statements"
    })

@app.get("/users-database", response_class=HTMLResponse)
async def users_database(request: Request, token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    return templates.TemplateResponse("users_database.html", {
        "request": request,
        "token": token,
        "page_title": "База данных пользователей по городам",
        "active_page": "users-database"
    })

@app.get("/expenses", response_class=HTMLResponse)
async def expenses(request: Request, token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    return templates.TemplateResponse("expenses.html", {
        "request": request,
        "token": token,
        "page_title": "Расходы",
        "active_page": "expenses"
    })

@app.get("/registration-requests", response_class=HTMLResponse)
async def registration_requests(request: Request, token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    # Отримуємо всі заявки зі статусом pending
    result = await db.execute(
        select(RegistrationRequest)
        .where(RegistrationRequest.status == "pending")
        .order_by(RegistrationRequest.created_at.desc())
    )
    requests = result.scalars().all()
    
    return templates.TemplateResponse("registration_requests.html", {
        "request": request,
        "token": token,
        "requests": requests,
        "page_title": "Заявки на реєстрацію",
        "active_page": "registration"
    })

@app.post("/api/registration-requests/{request_id}/approve")
async def approve_registration(request_id: int, token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    # Отримуємо заявку
    result = await db.execute(
        select(RegistrationRequest).where(RegistrationRequest.id == request_id)
    )
    reg_request = result.scalar_one_or_none()
    
    if not reg_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if reg_request.status != "pending":
        raise HTTPException(status_code=400, detail="Request already processed")
    
    # Створюємо користувача
    new_user = User(
        tg_id=reg_request.tg_id,
        username=reg_request.username,
        password_hash=reg_request.password_hash,
        city_id=reg_request.city_id,
        is_active=True
    )
    
    db.add(new_user)
    
    # Оновлюємо статус заявки
    reg_request.status = "approved"
    
    await db.commit()
    
    return {"status": "success", "message": "User approved"}

@app.post("/api/registration-requests/{request_id}/reject")
async def reject_registration(request_id: int, token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    # Отримуємо заявку
    result = await db.execute(
        select(RegistrationRequest).where(RegistrationRequest.id == request_id)
    )
    reg_request = result.scalar_one_or_none()
    
    if not reg_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if reg_request.status != "pending":
        raise HTTPException(status_code=400, detail="Request already processed")
    
    # Оновлюємо статус заявки
    reg_request.status = "rejected"
    
    await db.commit()
    
    return {"status": "success", "message": "Request rejected"}


# API для роботи з товарами
class ProductCreate(BaseModel):
    code: str
    name: str
    flavor: str | None = None
    purchase_price: float
    purchase_quantity: int
    sale_price: float
    city_id: int

class ProductUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    flavor: str | None = None
    purchase_price: float | None = None
    purchase_quantity: int | None = None
    sale_price: float | None = None
    sold_quantity: int | None = None
    stock: int | None = None


@app.get("/api/cities/{city_id}/products")
async def get_city_products(city_id: int, token: str, search: str = "", db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    query = select(Product).where(Product.city_id == city_id)
    
    if search:
        query = query.where(
            (Product.name.ilike(f"%{search}%")) | 
            (Product.code.ilike(f"%{search}%"))
        )
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "code": p.code,
            "name": p.name,
            "flavor": p.flavor,
            "purchase_price": p.purchase_price,
            "purchase_quantity": p.purchase_quantity,
            "sale_price": p.sale_price,
            "sold_quantity": p.sold_quantity,
            "avg_sale_price": p.avg_sale_price,
            "stock": p.stock
        }
        for p in products
    ]


@app.post("/api/products")
async def create_product(product: ProductCreate, token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    new_product = Product(
        code=product.code,
        name=product.name,
        flavor=product.flavor,
        purchase_price=product.purchase_price,
        purchase_quantity=product.purchase_quantity,
        sale_price=product.sale_price,
        stock=product.purchase_quantity,
        city_id=product.city_id
    )
    
    db.add(new_product)
    await db.commit()
    
    return {"status": "success", "id": new_product.id}


@app.put("/api/products/{product_id}")
async def update_product(product_id: int, product: ProductUpdate, token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    db_product = result.scalar_one_or_none()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.code:
        db_product.code = product.code
    if product.name:
        db_product.name = product.name
    if product.flavor is not None:
        db_product.flavor = product.flavor
    if product.purchase_price:
        db_product.purchase_price = product.purchase_price
    if product.purchase_quantity is not None:
        db_product.purchase_quantity = product.purchase_quantity
    if product.sale_price:
        db_product.sale_price = product.sale_price
    if product.sold_quantity is not None:
        db_product.sold_quantity = product.sold_quantity
    if product.stock is not None:
        db_product.stock = product.stock
    
    await db.commit()
    
    return {"status": "success"}


@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int, token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    await db.execute(
        delete(Product).where(Product.id == product_id)
    )
    await db.commit()
    
    return {"status": "success"}


@app.get("/api/cities")
async def get_cities(token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    result = await db.execute(
        select(City).where(City.is_active == True)
    )
    cities = result.scalars().all()
    
    return [{"id": c.id, "name": c.name} for c in cities]


# API для роботи з замовленнями
@app.get("/api/cities/{city_id}/couriers")
async def get_city_couriers(city_id: int, token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    result = await db.execute(
        select(User).where(User.city_id == city_id, User.is_active == True)
    )
    users = result.scalars().all()
    
    return [{"id": u.id, "username": u.username, "tg_id": u.tg_id} for u in users]


class OrderCreate(BaseModel):
    city_id: int
    courier_id: int
    receiver_id: int
    delivery_time: str
    delivery_address: str
    products: str


@app.post("/api/orders")
async def create_order(order: OrderCreate, token: str, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    new_order = Order(
        city_id=order.city_id,
        courier_id=order.courier_id,
        receiver_id=order.receiver_id,
        delivery_time=datetime.fromisoformat(order.delivery_time),
        delivery_address=order.delivery_address,
        products=order.products,
        status="pending"
    )
    
    db.add(new_order)
    await db.commit()
    
    # Тут буде відправка повідомлення в Telegram
    # TODO: Додати відправку повідомлення
    
    return {"status": "success", "id": new_order.id}


@app.get("/api/orders")
async def get_orders(token: str, city_id: int | None = None, db: AsyncSession = Depends(get_db)):
    _ = require_admin(token)
    
    query = select(Order).order_by(Order.created_at.desc())
    
    if city_id:
        query = query.where(Order.city_id == city_id)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    return [
        {
            "id": o.id,
            "city": o.city.name,
            "courier": o.courier.username,
            "receiver": o.receiver.username,
            "delivery_time": o.delivery_time.isoformat(),
            "delivery_address": o.delivery_address,
            "products": o.products,
            "status": o.status,
            "created_at": o.created_at.isoformat()
        }
        for o in orders
    ]
