from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import Message
from database.Database import DataBase
from core.dictionary import start_order_text, order_text


order_router = Router()


# Обработчик команды /order
@order_router.message(or_f(F.text == '/order', F.text == f'{start_order_text}'))
async def order_view(message: Message, bot: Bot):
    db = DataBase()
    orders = await db.get_orders(message.from_user.id)
    # Если есть заказы
    if orders:
        # Отправка пользователю
        await bot.send_message(message.from_user.id, 'Список Ваших заказов ⤵️:')
        order_statuses = {
            0: '🔅 Заказ оформлен',
            1: '🔆 Заказ отправлен',
            2: '✅ Заказ доставлен',
        }
        # Цикл для отправки всех заказов
        for order in orders:
            status = order_statuses.get(order.order_status)
            await bot.send_message(message.from_user.id, order_text % (order.id, status, order.sum_order, order.order_product))
    else:
        await bot.send_message(message.from_user.id, 'Заказов нет')