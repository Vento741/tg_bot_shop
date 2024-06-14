from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import Message, CallbackQuery, LabeledPrice
from handlers.start.start_kb import start_kb
from core.dictionary import *
from database.Database import DataBase
from handlers.basket.basket_kb import *
import os

basket_router = Router()

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


@basket_router.message(F.text == kb_clear_basket)
async def basket_delete_all(message: Message, bot: Bot):
    db = DataBase()
    await db.delete_basket_all(message.from_user.id)
    await bot.send_message(message.from_user.id, f'{basket_ok_delete_full}', reply_markup=start_kb())


@basket_router.message(F.text == kb_go_decoration)
async def basket_buy(message: Message, bot: Bot):
    db = DataBase()
    all_product = await db.get_basket(message.from_user.id)
    if all_product:
        num_product = 0
        summ_order = 0
        order_id = []
        for item in all_product:
            num_product += 1
            summ_order = summ_order + int(item.product_sum)
            order_id.append(item.product)
            product_list = []
            for product_id in order_id:
                products = await db.get_product_one(product_id)
                product_list.append(products.name)
            product_name = '\n'.join(product_list)
        await bot.send_message(message.from_user.id, basket_order_check % (num_product, product_name, summ_order), reply_markup=order_basket(order_id, summ_order))
    else:
        await bot.send_message(message.from_user.id, 'Ваша корзина пуста', reply_markup=start_kb())


@basket_router.callback_query(F.data.startswith('buybasket_'))
async def form_buy_basket(call: CallbackQuery):
    db = DataBase()
    all_product = await db.get_basket(call.from_user.id)
    product_list = []
    for product in all_product:
        item = await db.get_product_one(product.product)
        product_list.append(item.name)
    product_name = '\n'.join(product_list)
    await call.answer()
    summ = int(call.data.split('_')[-1])
    await call.bot.send_invoice(
        chat_id=call.from_user.id,
        title=f'Оформить заказ',
        description=f'Форма оплаты для товаров отложенных в корзине',
        provider_token=os.getenv('TOKEN_YOUKASSA'),
        payload=f'basket_{"_".join(str(item.id) for item in all_product)}',
        currency='rub',
        prices=[
            LabeledPrice(
                label=f'Оформить заказ',
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