from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.filters import or_f
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.start.start_kb import *
from handlers.start.register_state import *
from database.Database import DataBase
import re


start_router = Router()


@start_router.message(Command(commands=["start"]))
async def start(message: Message, bot: Bot):
    db = DataBase()
    if not await db.get_user(message.from_user.id):
        await bot.send_message(message.from_user.id, register_message, reply_markup=register_kb())
    else:
        await bot.send_message(message.from_user.id, start_message, reply_markup=start_kb())


@start_router.callback_query(F.data.startswith("register"))
async def start_register(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Укажите Ваше имя")
    await state.set_state(RegisterState.name)
    await call.answer()



@start_router.message(RegisterState.name)
async def username_input(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(name=message.text)
    db = DataBase()
    reg_data = await state.get_data()
    await db.add_user(reg_data["name"], message.from_user.id)
    await bot.send_message(message.from_user.id, f"Вы зарегистрировались как {reg_data['name']}", reply_markup=start_kb())
    await state.clear()

@start_router.message(or_f(F.text == '/politica', F.text == f'{politica}'))
async def show_rules(message: Message):
    await message.answer(rules_text, reply_markup=start_kb())  # Отправляем текст правил и клавиатуру