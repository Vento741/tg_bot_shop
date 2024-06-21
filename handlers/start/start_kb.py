from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from core.dictionary import *



def register_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text=register_kb_text, callback_data="register")
    return kb.as_markup()

def start_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text=f'{start_catalog_text}')
    kb.button(text=f'{start_basket_text}')
    kb.adjust(2)
    kb.button(text=f'{start_order_text}')
    kb.button(text=f'{politica}')

    return kb.as_markup(resize_keyboard=True)