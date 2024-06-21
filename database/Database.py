from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.models import *
import os


class DataBase:
    def __init__(self):
        """
        Инициализация подключения к базе данных
        """
        self.dp_host = os.getenv("DB_HOST")
        self.dp_user = os.getenv("DB_USER")
        self.dp_password = os.getenv("DB_PASSWORD")
        self.dp_name = os.getenv("DB_NAME")
        self.connect = f'postgresql+asyncpg://{self.dp_user}:{self.dp_password}@{self.dp_host}/{self.dp_name}'
        self.async_engine = create_async_engine(self.connect)
        self.Session = async_sessionmaker(bind=self.async_engine, class_=AsyncSession)
    

    async def drop_and_create_db(self):
        """
        Функция для удаления и создания базы данных
        """
        async with self.async_engine.begin() as conn:
            # Удаляем все таблицы
            await conn.run_sync(Base.metadata.drop_all)
            # # Создаем таблицы заново
            await conn.run_sync(Base.metadata.create_all)

    
    async def get_user(self, user_id):
        """
        Получить пользователя по ID
        """
        # Функция для получения пользователя
        async with self.Session() as request:
            result = await request.execute(select(User).where(User.telegram_id == user_id))
        return result.scalar()
    

    async def add_user(self, name, telegram_id):
        """
        Функция для добавления пользователя
        """
        async with self.Session() as request:
            request.add(User(
                username=name,
                telegram_id=telegram_id
            ))
            await request.commit()

    
    async def get_admin(self, admin_id):
        """
        Получить админа по ID
        """
        async with self.Session() as request:
            result = await request.execute(select(Admin).where(Admin.telegram_id == admin_id))  # Исправлено
            return result.scalar()
    

    async def get_admins(self):
        """
        Получить всех админов
        """
        async with self.Session() as request:
            result = await request.execute(select(Admin))
            return result.scalars().all()


    async def get_table(self, table_name):
        """
        Функция для получения таблиц
        """
        # Функция для получения таблиц
        async with self.Session() as request:
            result = await request.execute(select(table_name))
            return result.scalars().all()
        

    async def get_async_session(self):
        """Асинхронная функция для получения сессии SQLAlchemy."""
        async_session = async_sessionmaker(self.async_engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            yield session


    async def add_product(self, name, category_id, images, description, price, quantity, links):
        """Функция для добавления продукта."""
        async for session in self.get_async_session():  # Получаем асинхронную сессию
            async with session.begin():  # Начинаем транзакцию
                product = Products(
                    name=name,
                    category_id=category_id,
                    images=images,
                    description=description,
                    price=price,
                    quantity=quantity
                )
                session.add(product)
                await session.flush()  # Сохраняем продукт, чтобы получить его id

                # Создаем ссылки на товар
                for link in links:
                    session.add(ProductLink(product_id=product.id, link=link))
                await session.commit()  # Коммитим изменения
    

    async def get_product(self, category_id):
        """Функция для получения продуктов."""
        async with self.Session() as request:
            result = await request.execute(select(Products).where(Products.category_id == category_id))
        return result.scalars().all()
    

    async def check_basket(self, user_id, product_id):
        """Функция для проверки наличия продукта в корзине."""
        async with self.Session() as request:
            result = await request.execute(select(Basket).where(
                                           (Basket.user_telegram_id == user_id) & 
                                            (Basket.product == product_id)
            ))
        return result.scalars().all()
    

    async def get_product_one(self, id):
        """Функция для получения одного продукта."""
        async with self.Session() as request:
            result = await request.execute(select(Products).where(Products.id == id))
        return result.scalar()
    

    async def add_basket(self, telegram_id, product, product_price, quantity):
        """Функция для добавления продукта в корзину."""
        async with self.Session() as request:
            request.add(Basket(
                user_telegram_id=telegram_id,
                product=product,
                product_sum=product_price,
                quantity=quantity
            ))
            await request.commit()

    
    async def delete_basket_one(self, basket_id, user_id):
        """Функция для удаления одного продукта из корзины."""
        async with self.Session() as request:
            await request.execute(delete(Basket).where(Basket.id == basket_id, 
                                                    Basket.user_telegram_id == user_id))
            await request.commit()


    async def delete_basket_all(self, user_id):
        """Функция для удаления всех продуктов из корзины."""
        async with self.Session() as request:
            await request.execute(delete(Basket).where(Basket.user_telegram_id == user_id))
            await request.commit()

    
    async def add_order(self, order_sum, product_id, user_id, order_status):
        """Функция для добавления заказа."""
        async with self.Session() as request:
            request.add(Order(
                sum_order=order_sum,
                order_product=product_id,
                user_telegram_id=user_id,
                order_status=order_status
            ))
            await request.commit()


    async def get_basket(self, user_id):
        """Функция для получения корзины."""
        async with self.Session() as request:
            result = await request.execute(select(Basket).where(Basket.user_telegram_id == user_id))
        return result.scalars().all()
    

    async def get_orders(self, user_id):
        """Функция для получения заказов."""
        async with self.Session() as request:
            result = await request.execute(select(Order).where(
                            Order.user_telegram_id == user_id))
        return result.scalars().all()
    

    async def update_product_links(self, product_id, new_links):
        """Функция для обновления ссылок на продукт."""
        async with self.Session() as request:
            await request.execute(
                update(Products)
                .where(Products.id == product_id)
                .values(links=new_links)
            )
            await request.commit()

    async def get_product_links(self, product_id):
        """Функция для получения ссылок на продукт."""
        async with self.Session() as request:
            result = await request.execute(select(ProductLink).where(ProductLink.product_id == product_id))
            return result.scalars().all()


    async def delete_product_link_by_link(self, link):
        """Функция для удаления ссылки на продукт."""
        async with self.Session() as request:
            await request.execute(delete(ProductLink).where(ProductLink.link == link))
            await request.commit()


    async def delete_from_basket_by_quantity(self, user_id, product_id, quantity):
        """Функция для удаления продукта из корзины по количеству."""
        async with self.Session() as request:
            # Находим записи в корзине пользователя с заданным product_id
            items_to_delete = await request.execute(
                select(Basket)
                .where(Basket.user_telegram_id == user_id, Basket.product == product_id)
                .order_by(Basket.id)
            )
            items_to_delete = items_to_delete.scalars().all()

            deleted_count = 0
            for item in items_to_delete:
                if deleted_count >= quantity:
                    break

                await request.delete(item)  # Удаляем запись из корзины
                deleted_count += item.quantity

            await request.commit()

    async def decrease_product_quantity(self, product_id, quantity):
        """Функция для уменьшения количества продукта в каталоге."""
        async with self.Session() as request:
            product = await request.get(Products, product_id)
            if product:
                product.quantity -= quantity
                await request.commit()

    async def get_basket_quantity(self, user_id, product_id):
        """Функция для получения количества продукта в корзине."""
        async with self.Session() as request:
            result = await request.execute(
                select(Basket.quantity)
                .where(Basket.user_telegram_id == user_id, Basket.product == product_id)
            )
            return result.scalar()
    

    