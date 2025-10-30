from datetime import datetime
from sqlalchemy import BigInteger, String, Boolean, DateTime, Text, func, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base

class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True
    )


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True
    )

    products: Mapped[list["Product"]] = relationship(back_populates="city")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(255))
    flavor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    purchase_price: Mapped[float] = mapped_column(Float)
    purchase_quantity: Mapped[int] = mapped_column(Integer, default=0)
    sale_price: Mapped[float] = mapped_column(Float)
    sold_quantity: Mapped[int] = mapped_column(Integer, default=0)
    avg_sale_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), index=True)
    city: Mapped["City"] = relationship(back_populates="products")
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(Text)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), index=True)
    city: Mapped["City"] = relationship()
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True
    )


class RegistrationRequest(Base):
    __tablename__ = "registration_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(Text)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), index=True)
    city: Mapped["City"] = relationship()
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, approved, rejected
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True
    )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), index=True)
    city: Mapped["City"] = relationship()
    courier_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    courier: Mapped["User"] = relationship(foreign_keys=[courier_id])
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    receiver: Mapped["User"] = relationship(foreign_keys=[receiver_id])
    delivery_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    delivery_address: Mapped[str] = mapped_column(Text)
    products: Mapped[str] = mapped_column(Text)  # JSON string
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, delivered, cancelled
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True
    )
