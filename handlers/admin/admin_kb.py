from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database.Database import DataBase
from database.models import Category


# Клавиатура для создания продукта в категории
async def category_kb():
    db = DataBase()
    kb = InlineKeyboardBuilder()
    cats = await db.get_table(Category)
    for cat in cats:
        kb.button(text=f'{cat.name}', callback_data=f'select_{cat.name}_{cat.id}')
    kb.adjust(1)
    return kb.as_markup()


cancel_kb = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="Отмена")
    ]
], resize_keyboard=True, one_time_keyboard=True)

