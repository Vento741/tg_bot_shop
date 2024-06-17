from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from core.dictionary import *


def delete_basket(message_id, basket_id):  # Изменил аргумент на basket_id
    kb = InlineKeyboardBuilder()
    kb.button(text=f'{kb_delete_basket}', callback_data=f'd_basket_{message_id}_{basket_id}')  # Используем basket_id
    kb.adjust(1)
    return kb.as_markup()


def basket_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text=f'{kb_go_decoration}')
    kb.button(text=f'{kb_clear_basket}')
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


def order_basket(order_ids, summ):  # Добавляем аргумент order_ids
    kb = InlineKeyboardBuilder()
    kb.button(text=f'{kb_go_pay}', callback_data=f'buybasket_{summ * 100}_{"_".join(str(id) for id in order_ids)}')  # Добавляем order_ids в callback_data
    kb.adjust(1)
    return kb.as_markup()

# def order_basket(order_ids, summ):
#     kb = InlineKeyboardBuilder()
#     kb.button(text=f'{kb_go_pay}', callback_data=f'buybasket_{int(summ)}_{"_".join(str(id) for id in order_ids)}')  # Преобразуем summ в int
#     kb.adjust(1)
#     return kb.as_markup()