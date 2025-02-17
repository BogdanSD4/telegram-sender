from aiogram.fsm.storage.base import StorageKey
from apscheduler.jobstores.base import JobLookupError

from base.bot_init import bot
from base.scheduler_init import scheduler
from base.storage_init import storage
from config import cfg


async def post_task(post_name: str):
    storage_key = StorageKey(bot_id=bot.id, user_id=cfg.ADMIN_USER_ID, chat_id=cfg.ADMIN_USER_ID)
    user_data = await storage.get_data(storage_key)

    if 'posts' not in user_data or post_name not in user_data['posts']:
        return

    if 'chats' in user_data and len(user_data['chats']):
        chats = user_data['chats'].keys()
        post = user_data['posts'][post_name]

        if 'create' not in post:
            return

        for chat_id in chats:
            await bot.send_message(
                chat_id=chat_id,
                text=post['text']
            )

        post['period_time'] -= post['frequency_time']
        if post['period_time'] <= 0:
            del user_data['posts'][post_name]
            delete_post_task(post_name)

    await storage.set_data(storage_key, user_data)


def delete_post_task(post_name: str):
    try:
        scheduler.remove_job(job_id=post_name)
    except JobLookupError:
        pass


async def create_post_task(post_name: str, frequency_time: float):
    delete_post_task(post_name)

    scheduler.add_job(
        post_task,
        trigger='interval',
        seconds=frequency_time,
        args=[post_name],
        id=post_name
    )
