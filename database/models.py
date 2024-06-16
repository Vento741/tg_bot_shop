from sqlalchemy import Integer, String, Float, Text, BIGINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import BigInteger


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    userphone: Mapped[str] = mapped_column(String(100))
    telegram_id: Mapped[BigInteger] = mapped_column(BigInteger)


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    telegram_id: Mapped[BigInteger] = mapped_column(BigInteger)


class Products(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    category_id: Mapped[int] = mapped_column(Integer)
    images: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float)
    key_product: Mapped[str] = mapped_column(String(100))
    status_product: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer, default=0)

class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))


class Basket(Base):
    __tablename__ = "basket"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_telegram_id: Mapped[BigInteger] = mapped_column(BigInteger)
    product: Mapped[int] = mapped_column(Integer)
    product_sum: Mapped[float] = mapped_column(Float)


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sum_order: Mapped[float] = mapped_column(Float)
    order_product: Mapped[str] = mapped_column(Text)
    user_telegram_id: Mapped[BigInteger] = mapped_column(BigInteger)
    order_status: Mapped[int] = mapped_column(Integer)