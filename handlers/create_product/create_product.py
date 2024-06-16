from aiogram import Bot, Router, F
from aiogram.filters import or_f
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from database.Database import DataBase

from filters.check_admin import CheckAdmin
from core.dictionary import *
from handlers.create_product.create_product_kb import category_kb, cancel_kb
from handlers.create_product.create_product_state import CreateState



create_router = Router()


# Обработчик команды отмены
@create_router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await bot.send_message(message.from_user.id, cmd_cancel_text)


# Нажатие на кнопку "Добавить товар"
@create_router.message(or_f(F.text == '/create_product', F.text == 'Добавить товар')) #CheckAdmin()
async def cmd_create_product(message: Message, state: FSMContext, bot: Bot):
    await bot.send_message(message.from_user.id, f'Выберите категорию', reply_markup=await category_kb())
    await state.set_state(CreateState.category_product)


# Обработчик нажатия на категорию
@create_router.callback_query(CreateState.category_product)
async def select_category(call: CallbackQuery, state: FSMContext):
    category_name = call.data.split('_')[1]
    category_id = int(call.data.split('_')[-1])
    await call.message.answer(category_create_product % category_name)
    await state.update_data(category_product=category_id)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()
    await state.set_state(CreateState.name_product)


# Обработчик ввода названия
@create_router.message(CreateState.name_product)
async def product_name(message: Message, state: FSMContext, bot: Bot):
    await bot.send_message(message.from_user.id, img_createproduct, reply_markup=cancel_kb)
    await state.update_data(product_name=message.text)
    await state.set_state(CreateState.img_product)


# Обработчик прикрепления картинки
@create_router.message(CreateState.img_product)
async def input_product_img(message: Message, state: FSMContext, bot: Bot):
    if message.photo is not None:
        await bot.send_message(message.from_user.id, image_susses)
        await state.update_data(img_product=message.photo[-1].file_id)
        await state.set_state(CreateState.description_product)
    else:
        await bot.send_message(message.from_user.id, 'Нужно прикрепить картинку')


# Обработчик ввода описания
@create_router.message(CreateState.description_product)
async def input_product_description(message: Message, state: FSMContext, bot: Bot):
    await bot.send_message(message.from_user.id, (f'Описание сохранено \n\n'
                                          'Теперь введите цену'))
    await state.update_data(description_product=message.text)
    await state.set_state(CreateState.price_product)


# Обработчик ввода цены
@create_router.message(CreateState.price_product)
async def input_product_price(message: Message, state: FSMContext, bot: Bot):
    if message.text.isdigit():
        price = float(message.text)
        await state.update_data(price_product=price)
        await state.set_state(CreateState.key_product)
        await bot.send_message(message.from_user.id, createproduct_price)
    else:
        await bot.send_message(message.from_user.id, 'Нужно ввести целое число')


# Обработчик ввода ключа
@create_router.message(CreateState.key_product)
async def create_finish(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(key_product=message.text)
    product = await state.get_data()
    status = 0
    try:
        db = DataBase()
        await db.add_product(product['product_name'], product['category_product'],
                             product['img_product'], product['description_product'],
                             product['price_product'], product['key_product'], status)
        await bot.send_message(message.from_user.id, create_finish_text, reply_markup=None)
    except Exception as e:
        print(f'Ошибка при добавлении данных в таблицу: {e}')
        await bot.send_message(message.from_user.id, error_create_finish_text, reply_markup=None)
    finally:
        await state.clear()