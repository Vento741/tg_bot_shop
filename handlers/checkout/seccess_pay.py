import json
from aiogram import Bot
from aiogram.types import Message, PreCheckoutQuery
from database.Database import DataBase
import logging


logging.basicConfig(level=logging.INFO)



async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)


# Обработчик успешной оплаты
async def success_payment(message: Message, bot: Bot):
    user_id = message.from_user.id
    order_sum = message.successful_payment.total_amount // 100
    payload_parts = message.successful_payment.invoice_payload.split('_')
    order_status = 0
    user_name = message.successful_payment.order_info.name
    db = DataBase()

    # Проверяем тип оплаты (из корзины или напрямую)
    if payload_parts[0] == 'basket':
        product_ids = [int(id) for id in payload_parts[1].split(',')]
    else:
        product_ids = [int(payload_parts[1])]

    links = []  # Список для хранения ссылок

    # Обрабатываем каждый продукт
    for product_id in product_ids:
        product = await db.get_product_one(product_id)
        if product is not None:
            product_name = product.name
            await db.add_order(order_sum, product_name, user_id, order_status)

            msg = (f'У нас новый заказ!\n\n'
                   f'Заказчик: {user_name} (ID: {user_id})\n\n'
                   f'Товар: \n\n {product.name}\n'
                   f'Сумма заказа: {order_sum}')

            # Отправляем сообщение всем админам
            admins = await db.get_admins()
            for admin in admins:
                await bot.send_message(admin.telegram_id, msg)

            # Получаем ссылки на товар
            product_links = await db.get_product_links(product_id)
            links.extend([link.link for link in product_links])

            # Удаляем ссылки из базы данных
            await db.delete_product_links(product_id)
        else:
            logging.error(f"Продукт с ID {product_id} не найден")
            await bot.send_message(user_id,
                                   "Произошла ошибка при обработке заказа. Пожалуйста, обратитесь к администратору.")
            return  # Прерываем обработку, если продукт не найден

    # Отправляем все ссылки пользователю
    if links:
        await bot.send_message(user_id, f'Вы успешно оплатили заказ!\nВот ваши ссылки:\n' + '\n'.join(links))

    # Очищаем корзину, если оплата была из корзины
    if payload_parts[0] == 'basket':
        await db.delete_basket_all(user_id)

    logging.info(f"Успешная оплата от пользователя {user_id}. Сумма: {order_sum}")