from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.Database import DataBase
from database.models import Category
from core.dictionary import *


async def category_kb():
    db = DataBase()
    kb = InlineKeyboardBuilder()
    cats = await db.get_table(Category)
    for cat in cats:
        kb.button(text=f'{cat.name}', callback_data=f'select_category_{cat.id}')
    kb.adjust(1)
    return kb.as_markup()


async def product_kb(product_id):
    kb = InlineKeyboardBuilder()
    kb.button(text=f'{kb_buy_oneclick}', callback_data=f'buy_one_{product_id}')
    kb.button(text=f'{kb_add_basket}', callback_data=f'add_basket_{product_id}')
    kb.adjust(1)
    return kb.as_markup()


def product_kb_basket(product_id):
    kb = InlineKeyboardBuilder()
    kb.button(text=f'{kb_buy_oneclick}', callback_data=f'buy_one_{product_id}')
    kb.button(text=f'{kb_delete_basket}', callback_data=f'delete_basket_{product_id}')
    kb.adjust(1)
    return kb.as_markup()