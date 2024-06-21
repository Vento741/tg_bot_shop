from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import Message, CallbackQuery, LabeledPrice
from database.models import Basket
from handlers.start.start_kb import start_kb
from core.dictionary import *
from database.Database import DataBase
from handlers.basket.basket_kb import *
import os

basket_router = Router()


# Обработчик команды /basket
@basket_router.message(or_f(F.text == '/basket', F.text == f'{start_basket_text}'))
async def home_basket(message: Message, bot: Bot):
    db = DataBase()
    products = await db.get_basket(message.from_user.id)
    if products:
        grouped_products = {}
        total_amount = 0
        for product in products:
            if product.product not in grouped_products:
                grouped_products[product.product] = {
                    'item': await db.get_product_one(product.product),
                    'quantity': 0
                }
            grouped_products[product.product]['quantity'] += product.quantity
            total_amount += product.product_sum * product.quantity

        basket_text = ''
        for product_id, data in grouped_products.items():
            item = data['item']
            quantity = data['quantity']
            basket_text += f'<b>{item.name}</b>\nКоличество: {quantity}\nНа сумму: {item.price * quantity} руб.\n\n'

            # Сначала отправляем сообщение и сохраняем результат в msg
            msg = await bot.send_message(message.from_user.id, basket_text)

            # Затем отправляем сообщение с кнопкой "Удалить", используя msg.message_id
            await bot.send_message(message.from_user.id, dictionary_card_product % (item.description, item.price * quantity),
                                   reply_markup=delete_basket(msg.message_id, product.id))

            # Отправляем кнопку "Перейти к оплате" для каждого товара
        for product_id, data in grouped_products.items():
            item = data['item']
            quantity = data['quantity']
            # Отправляем кнопку "Оформить заказ" для каждого товара
            await bot.send_message(message.from_user.id, f'Оформить заказ на {item.name} ({quantity} шт.)',
                                   reply_markup=order_basket(product_id, item.price * quantity, quantity))

    else:
        await bot.send_message(message.from_user.id, f'{basket_null}', reply_markup=start_kb())

# Обработчик нажатия на "Удалить из корзины"
@basket_router.callback_query(F.data.startswith('d_basket_'))
async def basket_delete_one(call: CallbackQuery, bot: Bot):
    _, _, message_id, basket_id = call.data.split('_')
    message_id = int(message_id)
    basket_id = int(basket_id)
    db = DataBase()
    await db.delete_basket_one(basket_id, call.from_user.id)
    await call.message.answer(f'{basket_ok_delete}')
    await call.message.edit_reply_markup(reply_markup=None)
    await bot.delete_message(call.message.chat.id, message_id)  # Используем call.message.chat.id
    await call.answer()

# Если нажали "Очистить корзину"
@basket_router.message(F.text == kb_clear_basket)
async def basket_delete_all(message: Message, bot: Bot):
    db = DataBase()
    await db.delete_basket_all(message.from_user.id)
    await bot.send_message(message.from_user.id, f'{basket_ok_delete_full}', reply_markup=start_kb())


# Обработчик нажатия на " Перейти к оплате "
@basket_router.callback_query(F.data.startswith('buybasket_'))
async def form_buy_basket(call: CallbackQuery):
    db = DataBase()
    all_product = await db.get_basket(call.from_user.id)
    product_list = []
    for product in all_product:
        item = await db.get_product_one(product.product)
        product_list.append(item.name)
    product_name = '\n '.join(product_list)
    await call.answer()
    product_id = int(call.data.split('_')[1])  # Получаем ID товара из callback_data
    product = await db.get_product_one(product_id)
    quantity = await db.get_basket_quantity(call.from_user.id, product_id)  # Получаем количество товара в корзине

    await call.bot.send_invoice(
        chat_id=call.from_user.id,
        title=f'Оформить заказ',
        description=f'Форма оплаты для товаров отложенных в корзину',
        provider_token=os.getenv('TOKEN_YOUKASSA'),
        payload=f'basket_{product_id}_{quantity}',  # Передаём ID товара и quantity
        currency='rub',
        prices=[
            LabeledPrice(
                label=f'Оформить заказ',
                amount=int(product.price * quantity * 100)  # Рассчитываем сумму на основе цены товара и количества
            )
        ],
        start_parameter='Steam_magazine',
        provider_data=None,
        need_name=True,
        need_phone_number=False,
        need_email=False,
        need_shipping_address=False,
        is_flexible=False,
        disable_notification=False,
        protect_content=False,
        reply_to_message_id=None,
        reply_markup=None,
        request_timeout=60
    )
