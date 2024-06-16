import os
from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import CallbackQuery, Message, LabeledPrice
from database.models import Products
from handlers.catalog.catalog_kb import category_kb, product_kb, product_kb_basket
from aiogram.fsm.context import FSMContext

from core.dictionary import *
from database.Database import DataBase
from handlers.state.states import BuyStates, BasketStates


catalog_router = Router()


# Обработчик команды /catalog
@catalog_router.message(or_f(F.text == '/catalog', F.text == f'{start_catalog_text}'))
async def home_catalog(message: Message, bot: Bot):
    await bot.send_message(message.from_user.id, f'Выберите категорию', reply_markup=await category_kb())


# Обработчик нажатия на категорию
@catalog_router.callback_query(F.data.startswith('select_category_'))
async def category_catalog(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split('_')[-1])
    db = DataBase()
    products = await db.get_product(category_id)
    if products:
        for product in products:
            # Изменяем формат сообщения
            await call.message.answer_photo(
                photo=product.images,
                caption=f"<b>{product.name}</b>\n\n"
                        f"{product.description}\n\n"
                        f"Цена за шт: {product.price} руб.\n"
                        f"Доступное количество: {product.quantity}\n",
                reply_markup=await product_kb(product.id) if not await db.check_basket(call.from_user.id,
                                                                                       product.id) else await product_kb_basket(
                    product.id)
            )
    else:
        await call.message.answer(f'{category_not_found}')
    await call.answer()

# Обработчик кнопки "Купить в один клик"
@catalog_router.callback_query(F.data.startswith('buy_one_'))
async def buy_product(call: CallbackQuery, state: FSMContext):
    product_id = int(call.data.split('_')[-1])
    await state.set_state(BuyStates.ENTER_QUANTITY)
    await state.update_data(product_id=product_id)
    await call.message.answer("Введите количество товара:")


# Обработчик кнопки "Добавить в корзину"
@catalog_router.callback_query(F.data.startswith('add_basket_'))
async def add_basket(call: CallbackQuery, state: FSMContext):
    product_id = int(call.data.split('_')[-1])
    await state.set_state(BasketStates.ENTER_QUANTITY)
    await state.update_data(product_id=product_id)
    await call.message.answer("Введите количество товара:")


# Обработчик состояния ввода количества для корзины
@catalog_router.message(BasketStates.ENTER_QUANTITY)
async def process_quantity_basket(message: Message, state: FSMContext):
    try:
        quantity = int(message.text)
        data = await state.get_data()
        product_id = data.get('product_id')
        db = DataBase()
        product = await db.get_product_one(product_id)

        if product.quantity >= quantity:
            await db.add_basket(message.from_user.id, product_id, product.price, quantity)
            await state.finish()
            await message.answer(f"Добавлено {quantity} шт. товара {product.name} в корзину.")
        else:
            await message.answer(f"Недостаточно товара на складе. Доступно: {product.quantity} шт.")
    except ValueError:
        await message.answer("Некорректное количество. Введите целое число.")


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


# Функция для отправки информации о заказе
async def send_order_info(message: Message, bot: Bot, product: Products, quantity: int, order_sum: float):
    links = [product.key_product] * quantity  # Создаем список ссылок
    await bot.send_message(message.from_user.id,
                           f"Спасибо за покупку!\n"
                           f"Товар: {product.name}\n"
                           f"Количество: {quantity}\n"
                           f"Сумма: {order_sum} руб.\n"
                           f"Ссылки:\n" + "\n".join(links))
    # Отправка уведомлений администраторам
    db = DataBase()
    admins = await db.get_admins()
    for admin in admins:
        await bot.send_message(
            admin.telegram_id,
            f"Новый заказ!\n\n"
            f"Заказчик: {message.from_user.full_name} (ID: {message.from_user.id})\n"
            f"Товар: {product.name}\n"
            f"Количество: {quantity}\n"
            f"Сумма: {order_sum} руб."
        )    