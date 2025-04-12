import logging
import os

from aiogram.exceptions import TelegramBadRequest
from telethon import TelegramClient
from telethon.errors import AuthKeyUnregisteredError

from base.bot_init import bot
from config import cfg
from sessions.utils import session_path
from utils.blocker import block_user

USER_FAILED = "USER_FAILED"


def telethon_user(func):
    async def wrapper(client: str | TelegramClient, *args, **kwargs):
        no_disconnect = kwargs.get("no_disconnect", False)

        if isinstance(client, str):
            client = TelegramClient(session_path(client), cfg.API_ID, cfg.API_HASH)

        logging.info(f"TRY CONNECT")
        try:
            if not client.is_connected():
                await client.connect()

            result = await func(client, *args, **kwargs)
            logging.info(f"{client.session.filename} {func.__name__} -> {result}")

            if not no_disconnect:
                await client.disconnect()

            return result
        except (AuthKeyUnregisteredError, TelegramBadRequest):
            session_name = os.path.basename(client.session.filename.replace(".session", ""))

            await block_user(session_name)

            return USER_FAILED

    return wrapper
