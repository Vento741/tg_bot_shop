from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from core.dictionary import *
from database.Database import DataBase
from handlers.create_product.create_product_kb import *
import json

admin_router = Router()


class AddProduct(StatesGroup):
    ENTER_NAME = State()
    ENTER_CATEGORY = State()
    ENTER_IMAGES = State()
    ENTER_DESCRIPTION = State()
    ENTER_PRICE = State()
    ENTER_KEY = State()
    ENTER_QUANTITY = State()
    ENTER_LINKS = State()


@admin_router.message(F.text == '/admin')
async def admin_panel(message: Message, bot: Bot):
    db = DataBase()
    admin = await db.get_admin(message.from_user.id)
    if admin is not None:
        await bot.send_message(message.from_user.id, f'Выберите категорию для добавления товара:', reply_markup=await category_kb())  # Запрос выбора категории
    else:
        await bot.send_message(message.from_user.id, f'{admin_not_found}')


@admin_router.callback_query(F.data.startswith('add_product_category_'))
async def process_category_selection(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split('_')[-1])
    await state.update_data(category_id=category_id)  # Сохраняем выбранную категорию
    await state.set_state(AddProduct.ENTER_NAME)  # Запускаем процесс создания товара
    await call.message.answer(f'{admin_enter_name}')
    await call.answer()


@admin_router.message(AddProduct.ENTER_NAME)
async def enter_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProduct.ENTER_CATEGORY)
    await message.answer(f'{admin_enter_category}', reply_markup=await category_kb())


@admin_router.callback_query(F.data.startswith('add_product_category_'))
async def enter_category(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split('_')[-1])
    await state.update_data(category_id=category_id)
    await state.set_state(AddProduct.ENTER_IMAGES)
    await call.message.answer(f'{admin_enter_images}')
    await call.answer()


@admin_router.message(AddProduct.ENTER_IMAGES)
async def enter_images(message: Message, state: FSMContext):
    await state.update_data(images=message.text)
    await state.set_state(AddProduct.ENTER_DESCRIPTION)
    await message.answer(f'{admin_enter_description}')


@admin_router.message(AddProduct.ENTER_DESCRIPTION)
async def enter_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProduct.ENTER_PRICE)
    await message.answer(f'{admin_enter_price}')


@admin_router.message(AddProduct.ENTER_PRICE)
async def enter_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await state.set_state(AddProduct.ENTER_QUANTITY)  # Переходим к состоянию ввода количества
        await message.answer(f'{admin_enter_quantity}')  # Запрос количества
    except ValueError:
        await message.answer(f'{admin_error_price}')


@admin_router.message(AddProduct.ENTER_QUANTITY)
async def enter_quantity(message: Message, state: FSMContext):
    try:
        quantity = int(message.text)
        if quantity > 0:
            await state.update_data(quantity=quantity)
            await state.set_state(AddProduct.ENTER_LINKS)  # Переходим к состоянию ввода ссылок
            await message.answer(f'{admin_enter_links}')  # Запрос ссылок
        else:
            await message.answer(f'{admin_error_quantity}')
    except ValueError:
        await message.answer(f'{admin_error_quantity}')


@admin_router.message(AddProduct.ENTER_LINKS)
async def enter_links(message: Message, state: FSMContext):
    data = await state.get_data()
    links = message.text.split('\n')  # Разделяем ссылки по переносам строк
    if len(links) == data.get('quantity'):  # Проверяем количество ссылок
        await state.update_data(links=json.dumps(links))  # Сохраняем ссылки в JSON формате
        db = DataBase()
        await db.add_product(data.get('name'), data.get('category_id'), data.get('images'), data.get('description'),
                             data.get('price'), data.get('links'), data.get('quantity'))
        await state.finish()
        await message.answer(f'{admin_product_add}')
    else:
        await message.answer(
            f'Количество ссылок не совпадает с количеством товара. Введите {data.get("quantity")} ссылок, каждую на новой строке.')