from aiogram import Bot
from aiogram.types import Message, PreCheckoutQuery
from database.Database import DataBase


async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def success_payment(message: Message, bot: Bot):
    user_id = message.from_user.id
    order_sum = message.successful_payment.total_amount // 100
    product_id = int(message.successful_payment.invoice_payload.split('_')[-1])  # Получаем ID продукта
    order_status = 0
    user_name = f'{message.successful_payment.order_info.name}'
    db = DataBase()
    product = await db.get_product_one(product_id)
    product_name = product.name  # Получаем название продукта

    await db.add_order(order_sum, product_name, user_id, order_status)

    # Получаем продукт из базы данных по ID
    product = await db.get_product_one(product_id)

    msg = (f'У нас новый заказ!\n\n'
           f'Заказчик: {user_name} (ID: {message.from_user.id})\n\n'
           f'Товар: \n\n {product.name}\n'
           f'Сумма заказа: {order_sum}')
    admins = await db.get_admins()
    for admin in admins:
        await bot.send_message(admin.telegram_id, msg)
    
    # Отправляем ссылку пользователю
    
    await bot.send_message(message.from_user.id, f'Вы успешно оплатили заказ!\nВот ваш secret_key: {product.key_product}')
    
    

    if message.successful_payment.invoice_payload.split('_')[0] == 'basket':
        await db.delete_basket_all(message.from_user.id)
        await bot.send_message(message.from_user.id, 'Вы успешно оплатили заказ!\n'
                                                    'Вся корзина была очищена')
    else:
        await bot.send_message(message.from_user.id, 'Вы успешно оплатили заказ!')