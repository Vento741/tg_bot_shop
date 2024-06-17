import logging
from aiogram import Bot, Dispatcher, F
import asyncio
import os
from dotenv import load_dotenv
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
import signal

from database.Database import DataBase
# Подключаем роутеры
from handlers.start.start import start_router
from core.menu import set_commands
# from handlers.create_product.create_product import create_router
from handlers.admin.admin import admin_router
from handlers.catalog.catalog import catalog_router
from handlers.checkout.seccess_pay import *
from handlers.basket.basket import basket_router
from handlers.order.order import order_router



load_dotenv()

token = os.getenv("TOKEN_ID")

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def start_bot(bot: Bot):
    await bot.send_message(5161187711, text="Я запустил бота")

dp.startup.register(start_bot)
dp.include_router(start_router)
dp.include_router(admin_router)
dp.include_router(catalog_router)
dp.include_router(basket_router)
dp.include_router(order_router)

dp.pre_checkout_query.register(process_pre_checkout_query)
dp.message.register(success_payment, F.successful_payment)

async def start():
    try:
        db = DataBase()
        await db.drop_and_create_db()

        # Получаем текущий event loop
        loop = asyncio.get_running_loop()

        
        def signal_handler(signum, frame):
            logging.info("Остановка бота...")

            # Создаем список задач для ожидания
            tasks = [
                bot.close(),
                dp.stop_polling()
            ]

            # Ожидаем завершения всех задач
            asyncio.create_task(asyncio.gather(*tasks))

            # Останавливаем event loop после завершения задач
            loop.call_soon_threadsafe(loop.stop)

        signal.signal(signal.SIGINT, signal_handler)

        logging.info("Запуск бота...")
        await set_commands(bot)
        await dp.start_polling(bot, ship_updates=False)
    except KeyboardInterrupt:
        logging.info("Программа была остановлена пользователем.")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
    finally:
        await bot.session.close()



if __name__ == '__main__':
    asyncio.run(start())
