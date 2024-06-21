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

    # Получаем ID товара и количество
    product_id = int(payload_parts[1])
    quantity = int(payload_parts[2]) if len(payload_parts) > 2 else 1  # Получаем quantity, если она есть в payload

    # Обрабатываем товар
    product = await db.get_product_one(product_id)
    if product is not None:
        product_name = product.name
        await db.add_order(order_sum, product_name, user_id, order_status)

        # Получаем ссылки на оплаченные товары
        links_to_send = []
        links = await db.get_product_links(product_id)
        links_to_send.extend([link.link for link in links[:quantity]])

        # Отправляем ссылки пользователю
        await bot.send_message(user_id, f"Спасибо за покупку!\n"
                                       f"Товар: {product.name}\n"
                                       f"Количество: {quantity}\n"
                                       f"Сумма: {order_sum} руб.\n"
                                       f"Ссылки:\n" + "\n".join(links_to_send))

        # Отправляем уведомление администраторам
        msg = (f'У нас новый заказ!\n\n'
               f'Заказчик: {user_name} (ID: {user_id})\n\n'
               f'Товар: \n {product.name}\n'
               f'Количество: {quantity}\n'  # Добавляем \n
               f'Сумма заказа: {order_sum}')

        admins = await db.get_admins()
        for admin in admins:
            await bot.send_message(admin.telegram_id, msg)

        # Удаляем ссылки из БД (для всех типов покупок)
        links_to_delete = await db.get_product_links(product_id)
        for i in range(quantity):
            if links_to_delete:
                link_to_delete = links_to_delete.pop(0)
                await db.delete_product_link_by_link(link_to_delete.link)

        # Удаляем товар из корзины
        await db.delete_from_basket_quantity(user_id, product_id, quantity)

        # Уменьшаем количество товара в каталоге
        await db.decrease_product_quantity(product_id, quantity)

    logging.info(f"Успешная оплата от пользователя {user_id}. Сумма: {order_sum}")