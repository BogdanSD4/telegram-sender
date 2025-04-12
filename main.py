import asyncio
import base64
import json
import logging
import os.path

from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import BotCommand, Message

from base.bot_init import bot
from base.scheduler_init import scheduler
from base.storage_init import storage
from config import cfg
from scheduler.posts import create_post_task, delete_post_task
from sessions.session_manager import get_user_info, is_authorized
from sessions.user_controller import get_user_chats
from sessions.utils import get_session, delete_session
from utils.keyboards import main_menu_keyboard, authorization_menu_keyboard, users_menu_keyboard

from handlers.post import router as posts_router
from handlers.timer import router as timers_router
from handlers.chats import router as chats_router
from handlers.auth import router as auth_router
from handlers.admin import router as admin_router
from utils.schemas import State, StateSession

logging.basicConfig(level=logging.INFO)

dp = Dispatcher(storage=storage)

dp.include_routers(
    posts_router,
    timers_router,
    chats_router,
    auth_router,
    admin_router
)


@dp.message(Command("start", "menu"))
async def cmd_start(message: Message, state: FSMContext):
    if not cfg.ADMIN_USER_ID:
        return await message.answer(f"Your id: {message.from_user.id}")

    if message.from_user.id != cfg.ADMIN_USER_ID:
        return await message.answer(f"I can't help you, you are not my admin, id: {message.from_user.id}")

    data = State(await state.get_data())

    if not data.sessions or not data.selected_user_name:
        return await message.answer(f"Log in:", reply_markup=authorization_menu_keyboard(data))

    return await message.answer(f"Ready to work", reply_markup=main_menu_keyboard())


async def on_shutdown():
    storage_key = StorageKey(bot_id=bot.id, user_id=cfg.ADMIN_USER_ID, chat_id=cfg.ADMIN_USER_ID)
    user_data = State(await storage.get_data(storage_key))

    with open('save', 'w') as file:
        json_data = json.dumps(user_data.dict())
        encoded_text = base64.b64encode(json_data.encode()).decode()
        file.write(encoded_text)

    await bot.session.close()


async def start_scheduler(user_data: State) -> None:
    scheduler.start()

    for user_name, user in user_data.sessions.items():
        if not user.is_blocked and len(user.posts) > 0:

            for post_name, post in user.posts.copy().items():

                if post.period_time <= 0:
                    user.delete_post(post_name)
                    delete_post_task(f"{user_name}{post_name}")
                else:
                    await create_post_task(user_name, post_name, post.frequency_time)


async def check_user_sessions(user_data: State) -> None:
    sessions = set(get_session() + list(user_data.sessions.keys()))

    for user_name in sessions:
        if await is_authorized(user_name):
            session = StateSession()
            session.info = await get_user_info(user_name)
            session.chats = await get_user_chats(user_name)
            user_data.add_session(user_name, session)
        else:
            user_data.delete_session(user_name)
            delete_session(user_name)

    user_data.selected_user_name = None


async def main():
    # try:
        commands = [
            BotCommand(command="menu", description="Main menu"),
        ]
        await bot.set_my_commands(commands)

        if os.path.exists('save'):
            with open('save', 'r') as file:
                encoded_text = file.read()
                decoded_text = base64.b64decode(encoded_text.encode()).decode()
                user_data = State(json.loads(decoded_text))
        else:
            user_data = State()

        await start_scheduler(user_data)
        await check_user_sessions(user_data)

        storage_key = StorageKey(bot_id=bot.id, user_id=cfg.ADMIN_USER_ID, chat_id=cfg.ADMIN_USER_ID)
        await storage.set_data(storage_key, user_data.dict())

        await dp.start_polling(bot)
    # except Exception as e:
    #     logging.error(f"Ошибка: {e}")
    # finally:
        await on_shutdown()

if __name__ == "__main__":
    asyncio.run(main())
