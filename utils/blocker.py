from aiogram.fsm.storage.base import StorageKey

from base.bot_init import bot
from base.storage_init import storage
from config import cfg
from sessions.utils import get_session, delete_session
from utils.keyboards import authorization_menu_keyboard
from utils.schemas import State


async def block_user(user_name: str):
    storage_key = StorageKey(bot_id=bot.id, user_id=cfg.ADMIN_USER_ID, chat_id=cfg.ADMIN_USER_ID)
    user_data = State(await storage.get_data(storage_key))

    if user_name in user_data.sessions:
        user_data.sessions[user_name].is_blocked = True

    delete_session(user_name)

    await storage.set_data(storage_key, user_data.dict())
    await bot.send_message(
        chat_id=cfg.ADMIN_USER_ID,
        text=f'User named as "{user_name}" was blocked or unauthorized',
        reply_markup=authorization_menu_keyboard(user_data)
    )
