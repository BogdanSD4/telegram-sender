import asyncio
import logging

import redis
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand

from config import cfg
from utils.keyboards import main_menu_keyboard

from handlers.post import router as posts_router
from handlers.timer import router as timers_router

redis_client = redis.asyncio.Redis(host=cfg.REDIS_HOST, port=cfg.REDIS_PORT, decode_responses=True)
storage = RedisStorage(redis=redis_client, key_builder=DefaultKeyBuilder(with_bot_id=True))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=cfg.BOT_TOKEN)
dp = Dispatcher(storage=storage)

dp.include_routers(
    posts_router,
    timers_router,
)


@dp.message(Command("start", "menu"))
async def cmd_start(message: types.Message):
    if not cfg.ADMIN_USER_ID:
        return await message.answer(f"Your id: {message.from_user.id}")

    if message.from_user.id != cfg.ADMIN_USER_ID:
        return await message.answer(f"I can't help you, you are not my admin")

    return await message.answer(f"Ready to work", reply_markup=main_menu_keyboard())


async def on_shutdown():
    async with open('file.txt', 'w') as file:
        await file.write('dwedw')
    await bot.session.close()


async def main():
    try:
        commands = [
            BotCommand(command="menu", description="Main menu"),
        ]
        await bot.set_my_commands(commands)
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
    finally:
        await on_shutdown()

if __name__ == "__main__":
    asyncio.run(main())
