import asyncio

from telethon import TelegramClient

from media.media_manager import media_path, Media
from utils.decorators import telethon_user
from utils.schemas import StateChat, StatePost, StateSession


@telethon_user
async def get_user_chats(client: str | TelegramClient) -> dict[int, StateChat]:
    dialogs = await client.get_dialogs()

    return {
        dialog.id: StateChat({'name': dialog.title})
        for dialog in dialogs if dialog.title == '. & Комарнік Христина (кб)'
    }


@telethon_user
async def send_posts_by_user(client: str | TelegramClient, user: StateSession, post: StatePost):
    for chat_id in user.chats:
        chat_id = int(chat_id)
        if post.media:
            await client.send_file(
                entity=chat_id,
                file=media_path(post.media, post.media_type),
                caption=post.caption or '')
        else:
            await client.send_message(
                entity=chat_id,
                message=post.text
            )
        await asyncio.sleep(0.2)
