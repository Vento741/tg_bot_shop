from aiogram.filters import BaseFilter
from aiogram.types import Message
from database.Database import DataBase


class CheckAdmin(BaseFilter):
    async def __call__(self, message: Message):
        try:
            db = DataBase()
            return await db.get_admin(str(message.from_user.id))
        except:
            return False
    