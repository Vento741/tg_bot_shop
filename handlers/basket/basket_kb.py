from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from core.dictionary import *


def delete_basket(message_id, product_id):
    kb = InlineKeyboardBuilder()
    kb.button(text=f'{kb_delete_basket}', callback_data=f'd_basket_{message_id}_{product_id}')
    kb.adjust(1)
    return kb.as_markup()


def basket_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text=f'{kb_go_decoration}')
    kb.button(text=f'{kb_clear_basket}')
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


def order_basket(product_name, summ):
    kb = InlineKeyboardBuilder()
    kb.button(text=f'{kb_go_pay}', callback_data=f'buybasket_{summ}')
    kb.adjust(1)
    return kb.as_markup()