import asyncio
import base64
import json
import logging
import os.path

from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import BotCommand

from base.bot_init import bot
from base.scheduler_init import scheduler
from base.storage_init import storage
from config import cfg
from scheduler.posts import create_post_task
from utils.keyboards import main_menu_keyboard

from handlers.post import router as posts_router
from handlers.timer import router as timers_router
from handlers.chats import router as chats_router


logging.basicConfig(level=logging.INFO)

dp = Dispatcher(storage=storage)

dp.include_routers(
    posts_router,
    timers_router,
    chats_router
)


@dp.message(Command("start", "menu"))
async def cmd_start(message: types.Message):
    if not cfg.ADMIN_USER_ID:
        return await message.answer(f"Your id: {message.from_user.id}")

    if message.from_user.id != cfg.ADMIN_USER_ID:
        return await message.answer(f"I can't help you, you are not my admin")

    return await message.answer(f"Ready to work", reply_markup=main_menu_keyboard())


async def on_shutdown():
    storage_key = StorageKey(bot_id=bot.id, user_id=cfg.ADMIN_USER_ID, chat_id=cfg.ADMIN_USER_ID)
    user_data = await storage.get_data(storage_key)

    with open('save', 'w') as file:
        json_data = json.dumps(user_data)
        encoded_text = base64.b64encode(json_data.encode()).decode()
        file.write(encoded_text)

    await bot.session.close()


async def start_scheduler(user_data: dict) -> None:
    scheduler.start()

    if 'posts' in user_data and len(user_data['posts']) > 0:
        to_del = []
        for key, value in user_data['posts'].items():
            if value['period_time'] <= 0:
                to_del.append(key)
            else:
                await create_post_task(key, value['frequency_time'])

        for key in to_del:
            del user_data['posts'][key]


async def main():
    try:
        commands = [
            BotCommand(command="menu", description="Main menu"),
        ]
        await bot.set_my_commands(commands)

        if os.path.exists('save'):
            with open('save', 'r') as file:
                encoded_text = file.read()
                decoded_text = base64.b64decode(encoded_text.encode()).decode()
                user_data = json.loads(decoded_text)
        else:
            user_data = None

        await start_scheduler(user_data)

        storage_key = StorageKey(bot_id=bot.id, user_id=cfg.ADMIN_USER_ID, chat_id=cfg.ADMIN_USER_ID)
        await storage.set_data(storage_key, user_data)

        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
    finally:
        await on_shutdown()

if __name__ == "__main__":
    asyncio.run(main())
