import os
from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import CallbackQuery, Message, LabeledPrice
from handlers.catalog.catalog_kb import category_kb, product_kb, product_kb_basket

from core.dictionary import *
from database.Database import DataBase


catalog_router = Router()


# Обработчик команды /catalog
@catalog_router.message(or_f(F.text == '/catalog', F.text == f'{start_catalog_text}'))
async def home_catalog(message: Message, bot: Bot):
    await bot.send_message(message.from_user.id, f'Выберите категорию', reply_markup=await category_kb())


# Обработчик нажатия на категорию
@catalog_router.callback_query(F.data.startswith('select_category_'))
async def category_catalog(call: CallbackQuery):
    category_id = int(call.data.split('_')[-1])
    db = DataBase()
    products = await db.get_product(category_id)
    if products:
        for product in products:
            await call.message.answer_photo(photo=product.images, caption=f'{product.name}')
            if await db.check_basket(call.from_user.id, product.id):
                await call.message.answer(dictionary_card_product % (product.description, product.price),
                                          reply_markup= product_kb_basket(product.id))
            else:
                await call.message.answer(dictionary_card_product % (product.description, product.price),
                                          reply_markup= await product_kb(product.id))
    else:
        await call.message.answer(f'{category_not_found}')
    await call.answer()


# Обработчик нажатия на продукт
@catalog_router.callback_query(F.data.startswith('buy_one_'))
async def buy_product(call: CallbackQuery):
    await call.answer()
    product_id = int(call.data.split('_')[-1])
    db = DataBase()
    product = await db.get_product_one(product_id)
    await call.bot.send_invoice(
        chat_id=call.from_user.id,
        title=f'Купить {product.name}',
        description=f'Купить {product.name} по супер цене',
        provider_token=os.getenv('TOKEN_YOUKASSA'),
        payload=f'buy_{product.id}',
        currency='rub',
        prices=[
            LabeledPrice(
                label=f'купить {product.name}',
                amount=product.price * 100
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


# Обработчик нажатия на добавить в корзину
@catalog_router.callback_query(F.data.startswith('add_basket_'))
async def add_basket(call: CallbackQuery):
    product_id = int(call.data.split('_')[-1])
    db = DataBase()
    product = await db.get_product_one(product_id)
    await db.add_basket(call.from_user.id, product.id, product.price)
    await call.message.answer(f'Товар {product.name} добавлен в корзину')
    await call.message.edit_reply_markup(reply_markup=product_kb_basket(product_id))


# Обработчик нажатия на удалить из корзины
@catalog_router.callback_query(F.data.startswith('delete_basket_'))
async def delete_basket(call: CallbackQuery):
    product_id = int(call.data.split('_')[-1])
    db = DataBase()
    product = await db.get_product_one(product_id)
    await db.delete_basket_one(product_id, call.from_user.id)
    await call.message.answer(f'Товар {product.name} удален из корзины')
    await call.message.edit_reply_markup(reply_markup= await product_kb(product_id))
    await call.answer()