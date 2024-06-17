from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.models import *
import os


class DataBase:
    def __init__(self):
        self.dp_host = os.getenv("DB_HOST")
        self.dp_user = os.getenv("DB_USER")
        self.dp_password = os.getenv("DB_PASSWORD")
        self.dp_name = os.getenv("DB_NAME")
        self.connect = f'postgresql+asyncpg://{self.dp_user}:{self.dp_password}@{self.dp_host}/{self.dp_name}'
        self.async_engine = create_async_engine(self.connect)
        self.Session = async_sessionmaker(bind=self.async_engine, class_=AsyncSession)
    

    # Функция для удаления и создания базы данных
    async def drop_and_create_db(self):
        async with self.async_engine.begin() as conn:
            # Удаляем все таблицы
            await conn.run_sync(Base.metadata.drop_all)
            # # Создаем таблицы заново
            await conn.run_sync(Base.metadata.create_all)

    
    # Функции для работы с пользователями
    async def get_user(self, user_id):
        # Функция для получения пользователя
        async with self.Session() as request:
            result = await request.execute(select(User).where(User.telegram_id == user_id))
        return result.scalar()
    

    # Функция для добавления пользователя
    async def add_user(self, name, telegram_id):
        # Функция для добавления пользователя
        async with self.Session() as request:
            request.add(User(
                username=name,
                telegram_id=telegram_id
            ))
            await request.commit()

    
    # Функции для работы с админами
    async def get_admin(self, admin_id):
        async with self.Session() as request:
            result = await request.execute(select(Admin).where(Admin.telegram_id == admin_id))  # Исправлено
            return result.scalar()
    

    # Функция для получения всех админов
    async def get_admins(self):
        # Функция для получения всех админов
        async with self.Session() as request:
            result = await request.execute(select(Admin))
            return result.scalars().all()


    # Функции для работы с продуктами
    async def get_table(self, table_name):
        # Функция для получения таблиц
        async with self.Session() as request:
            result = await request.execute(select(table_name))
            return result.scalars().all()
        

    # Функция для добавления продукта
    async def add_product(self, name, category_id, images, description, price, quantity, links):
        # Функция для добавления продукта
        async with self.Session() as request:
            product = Products(
                name=name,
                category_id=category_id,
                images=images,
                description=description,
                price=price,
                quantity=quantity
            )
            request.add(product)
            await request.commit()
            # Создаем ссылки на товар
            for link in links:
                request.add(ProductLink(product_id=product.id, link=link))
            await request.commit()

    
    # Функции для работы с продуктами
    async def get_product(self, category_id):
        # Функция для получения продуктов
        async with self.Session() as request:
            result = await request.execute(select(Products).where(Products.category_id == category_id))
        return result.scalars().all()
    

    # Функция для проверки наличия продукта в корзине
    async def check_basket(self, user_id, product_id):
        # Функция для проверки наличия продукта в корзине
        async with self.Session() as request:
            result = await request.execute(select(Basket).where(
                                           (Basket.user_telegram_id == user_id) & 
                                            (Basket.product == product_id)
            ))
        return result.scalars().all()
    

    # Функции для работы с продуктами
    async def get_product_one(self, id):
        # Функция для получения продукта
        async with self.Session() as request:
            result = await request.execute(select(Products).where(Products.id == id))
        return result.scalar()
    

    # Функции для работы с корзиной
    async def add_basket(self, telegram_id, product, product_sum, quantity):
        # Функция для добавления продукта в корзину
        async with self.Session() as request:
            request.add(Basket(
                user_telegram_id=telegram_id,
                product=product,
                product_sum=product_sum,
                quantity=quantity
            ))
            await request.commit()

    
    # Функция для удаления продукта из корзины
    async def delete_basket_one(self, product_id, user_id):
        # Функция для удаления продукта из корзины
        async with self.Session() as request:
            await request.execute(delete(Basket).where(Basket.product == product_id,
                                                       Basket.user_telegram_id == user_id))
            await request.commit()


    # Функция для удаления всех продуктов из корзины
    async def delete_basket_all(self, user_id):
        # Функция для удаления всех продуктов из корзины
        async with self.Session() as request:
            await request.execute(delete(Basket).where(Basket.user_telegram_id == user_id))
            await request.commit()

    
    # Функция для добавления заказа
    async def add_order(self, order_sum, product_id, user_id, order_status):
        # Функция для добавления заказа
        async with self.Session() as request:
            request.add(Order(
                sum_order=order_sum,
                order_product=product_id,
                user_telegram_id=user_id,
                order_status=order_status
            ))
            await request.commit()


    # Функция для получения корзины
    async def get_basket(self, user_id):
        # Функция для получения корзины
        async with self.Session() as request:
            result = await request.execute(select(Basket).where(Basket.user_telegram_id == user_id))
        return result.scalars().all()
    

    # Функция для получения заказов
    async def get_orders(self, user_id):
        # Функция для получения заказов
        async with self.Session() as request:
            result = await request.execute(select(Order).where(
                            Order.user_telegram_id == user_id))
        return result.scalars().all()
    

    async def update_product_links(self, product_id, new_links):
        async with self.Session() as request:
            await request.execute(
                update(Products)
                .where(Products.id == product_id)
                .values(links=new_links)
            )
            await request.commit()

    async def get_product_links(self, product_id):
        async with self.Session() as request:
            result = await request.execute(select(ProductLink).where(ProductLink.product_id == product_id))
            return result.scalars().all()

    async def delete_product_links(self, product_id):
        async with self.Session() as request:
            await request.execute(delete(ProductLink).where(ProductLink.product_id == product_id))
            await request.commit()