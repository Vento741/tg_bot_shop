from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from core.dictionary import *
from database.Database import DataBase
from handlers.admin.admin_state import AddProduct
from handlers.admin.admin_kb import *
import json

admin_router = Router()


# Обработчик команды отмены
@admin_router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await bot.send_message(message.from_user.id, cmd_cancel_text)



@admin_router.message(F.text == '/admin')
async def admin_panel(message: Message, state: FSMContext, bot: Bot):
    db = DataBase()
    admin = await db.get_admin(message.from_user.id)
    if admin is not None:
        await state.update_data(db=db)  # Сохраняем db в state
        await bot.send_message(message.from_user.id, f'Выберите категорию для добавления товара:', reply_markup=await category_kb())  # Запрос выбора категории
        await state.set_state(AddProduct.ENTER_CATEGORY)
    else:
        await bot.send_message(message.from_user.id, f'{admin_not_found}')


@admin_router.callback_query(AddProduct.ENTER_CATEGORY)
async def process_category_selection(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split('_')[-1])
    await call.message.answer(f'{admin_enter_name}')
    await state.update_data(category_id=category_id)  # Сохраняем выбранную категорию
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()
    await state.set_state(AddProduct.ENTER_NAME)  # Запускаем процесс создания товара


@admin_router.message(AddProduct.ENTER_NAME)
async def enter_name(message: Message, state: FSMContext, bot: Bot):
    await bot.send_message(message.from_user.id, f'{admin_enter_images}', reply_markup=cancel_kb)
    await state.update_data(name=message.text)
    await state.set_state(AddProduct.ENTER_IMAGES)



@admin_router.message(AddProduct.ENTER_IMAGES)
async def enter_images(message: Message, state: FSMContext, bot: Bot):
    if message.photo is not None:
        await bot.send_message(message.from_user.id, f'{admin_enter_description}', reply_markup=cancel_kb)
        await state.update_data(images=message.photo[-1].file_id)
        await state.set_state(AddProduct.ENTER_DESCRIPTION)
    else:
        await bot.send_message(message.from_user.id, 'Нужно прикрепить картинку')

@admin_router.message(AddProduct.ENTER_DESCRIPTION)
async def enter_description(message: Message, state: FSMContext, bot: Bot):
    await bot.send_message(message.from_user.id, f'{admin_enter_price}', reply_markup=cancel_kb)
    await state.update_data(description=message.text)
    await state.set_state(AddProduct.ENTER_PRICE)


@admin_router.message(AddProduct.ENTER_PRICE)
async def enter_price(message: Message, state: FSMContext, bot: Bot):
    if message.text.isdigit():
        price = float(message.text)
        await state.update_data(price=price)
        await state.set_state(AddProduct.ENTER_QUANTITY)  # Переходим к состоянию ввода количества
        await message.answer(f'{admin_enter_quantity}')  # Запрос количества
    else:
        await message.answer(f'{admin_error_price}')


@admin_router.message(AddProduct.ENTER_QUANTITY)
async def enter_quantity(message: Message, state: FSMContext, bot: Bot):
    try:
        quantity = int(message.text)
        if quantity > 0:
            await state.update_data(quantity=quantity)
            await state.set_state(AddProduct.ENTER_LINKS)
            await message.answer(f'Введите {quantity} ссылок на товар, каждую на новой строке:')
        else:
            await message.answer(f'{admin_error_quantity}')
    except ValueError:
        await message.answer(f'{admin_error_quantity}')


@admin_router.message(AddProduct.ENTER_LINKS)
async def enter_links(message: Message, state: FSMContext):
    data = await state.get_data()
    links = message.text.split('\n')
    await state.update_data(links=links)  # Сохраняем ссылки в state
    data = await state.get_data()  # Получаем все данные из state

    if len(links) == data.get('quantity'):
        print("Содержимое data:", data)
        db = DataBase()
        await db.add_product(data.get('name'), data.get('category_id'), data.get('images'), data.get('description'),
                            data.get('price'), data.get('quantity'), data.get('links'))
        await state.clear()
        await message.answer(f'{admin_product_add}')
    else:
        await message.answer(
            f'Количество ссылок не совпадает с количеством товара. Введите {data.get("quantity")} ссылок, каждую на новой строке.')