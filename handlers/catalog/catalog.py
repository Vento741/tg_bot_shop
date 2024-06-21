import os
from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import CallbackQuery, Message, LabeledPrice
from database.models import Products
from handlers.catalog.catalog_kb import category_kb, product_kb, product_kb_basket
from aiogram.fsm.context import FSMContext

from core.dictionary import *
from database.Database import DataBase
from handlers.start.start_kb import start_kb
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
                                                                                       product.id) else product_kb_basket(
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
            await state.clear()
            await message.answer(f"Добавлено {quantity} шт. товара {product.name} в корзину.👍", reply_markup=start_kb())
        else:
            await message.answer(f"Недостаточно товара на складе. Доступно: {product.quantity} шт.\n\nОбязательно проверьте позже, скоро завезу 😌")
    except ValueError:
        await message.answer("Некорректное количество. Введите целое число.", reply_markup=start_kb())


# Обработчик состояния ввода количества для "Купить в один клик"
@catalog_router.message(BuyStates.ENTER_QUANTITY)
async def process_quantity_buy_one(message: Message, state: FSMContext):
    try:
        quantity = int(message.text)
        data = await state.get_data()
        product_id = data.get('product_id')
        db = DataBase()
        product = await db.get_product_one(product_id)

        if product.quantity >= quantity:
            # Отправляем инвойс для оплаты
            await message.answer("Переходим к оплате...")
            await message.bot.send_invoice(
                chat_id=message.from_user.id,
                title=f'Купить {product.name}',
                description=f'{product.description}',
                provider_token=os.getenv('TOKEN_YOUKASSA'),
                payload=f'product_{product_id}_{quantity}',  # Передаём ID товара и quantity
                currency='rub',
                prices=[
                    LabeledPrice(
                        label=f'Оплата товара',
                        amount=int(product.price * quantity * 100)  # Рассчитываем сумму
                    )
                ],
                start_parameter='buy_one_click',
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
            await state.clear()
        else:
            await message.answer(f"Недостаточно товара на складе. Доступно: {product.quantity} шт.\n\nОбязательно проверьте позже, скоро завезу 😌")
    except ValueError:
        await message.answer("Некорректное количество. Введите целое число.", reply_markup=start_kb())




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

