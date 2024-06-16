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
        for product in products:
            item = await db.get_product_one(product.product)
            msg = await bot.send_photo(message.from_user.id, photo=item.images, caption=f'<b>{item.name}</b>',
                                       reply_markup=basket_kb())
            await bot.send_message(message.from_user.id, dictionary_card_product % (item.description, item.price),
                                   reply_markup=delete_basket(msg.message_id, item.id))
    else:
        await bot.send_message(message.from_user.id, f'{basket_null}', reply_markup=start_kb())


# Обработчик нажатия на категорию
@basket_router.callback_query(F.data.startswith('d_basket_'))
async def basket_delete_one(call: CallbackQuery, bot: Bot):
    product_id = int(call.data.split('_')[-1])
    message_id = int(call.data.split('_')[-2])
    db = DataBase()
    await db.delete_basket_one(product_id, call.from_user.id)
    await call.message.answer(f'{basket_ok_delete}')
    await call.message.edit_reply_markup(reply_markup=None)
    await bot.delete_message(message_id, call.from_user.id)
    await call.answer()


# Если нажали "Очистить корзину"
@basket_router.message(F.text == kb_clear_basket)
async def basket_delete_all(message: Message, bot: Bot):
    db = DataBase()
    await db.delete_basket_all(message.from_user.id)
    await bot.send_message(message.from_user.id, f'{basket_ok_delete_full}', reply_markup=start_kb())


# Если нажали "Оформить заказ"
@basket_router.message(F.text == kb_go_decoration)
async def basket_buy(message: Message, bot: Bot):
    db = DataBase()
    all_products = await db.get_basket(message.from_user.id)
    if all_products:
        product_list = []
        total_amount = 0
        order_ids = []
        for item in all_products:
            product = await db.get_product_one(item.product)
            product_list.append(f"{product.name} ({item.quantity} шт.)")
            total_amount += item.product_sum * item.quantity
            order_ids.extend([item.product] * item.quantity)  # Добавляем ID продукта нужное количество раз
        product_names = '\n'.join(product_list)
        await bot.send_message(message.from_user.id,
                               basket_order_check % (len(all_products), product_names, total_amount),
                               reply_markup=order_basket(order_ids, total_amount))
    else:
        await bot.send_message(message.from_user.id, 'Ваша корзина пуста', reply_markup=start_kb())

# Обработчик нажатия на "Оформить заказ"
@basket_router.callback_query(F.data.startswith('buybasket_'))
@basket_router.callback_query(F.data.startswith('buybasket_'))
async def form_buy_basket(call: CallbackQuery):
    db = DataBase()
    all_products = await db.get_basket(call.from_user.id)
    product_list = []
    total_amount = 0
    order_ids = []
    for product in all_products:
        item = await db.get_product_one(product.product)
        product_list.append(item.name)
        total_amount += item.product_sum * product.quantity
        order_ids.extend([item.product] * product.quantity)  # Добавляем ID продукта нужное количество раз
    product_name = '\n'.join(product_list)
    await call.answer()
    summ = int(call.data.split('_')[-1])
    await call.bot.send_invoice(
        chat_id=call.from_user.id,
        title=f'Оформить заказ',
        description=f'Форма оплаты для товаров отложенных в корзине: {product_name}',
        provider_token=os.getenv('TOKEN_YOUKASSA'),
        payload=f'basket_{"_".join(str(id) for id in order_ids)}',  # Передаем все ID продуктов
        currency='rub',
        prices=[
            LabeledPrice(
                label=f'Оплата корзины',
                amount=summ * 100
            )
        ],
        start_parameter='Tg_MAGNAT_SHop',
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


async def add_basket(self, telegram_id, product, product_sum, quantity):
    async with self.Session() as request:
        request.add(Basket(
            user_telegram_id=telegram_id,
            product=product,
            product_sum=product_sum,
            quantity=quantity  # Добавляем количество
        ))
        await request.commit()