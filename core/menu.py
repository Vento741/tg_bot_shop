from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="start",
            description="Запустить бота / Вернуться в начало"
        ),
        BotCommand(
            command="catalog",
            description="Каталог"
        ),
        BotCommand(
            command="order",
            description="Посмотреть список заказов"
        ),
        BotCommand(
            command="basket",
            description="Корзина"
        )
    ]

    await bot.set_my_commands(commands,BotCommandScopeDefault())