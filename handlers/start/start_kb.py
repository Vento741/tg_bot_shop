from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from core.dictionary import *



def register_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text=register_kb_text, callback_data="register")
    return kb.as_markup()

def start_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text=start_catalog_text)
    kb.button(text=start_order_text)
    kb.button(text=start_basket_text)

    return kb.as_markup(resize_keyboard=True)