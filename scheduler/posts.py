from aiogram.fsm.storage.base import StorageKey
from apscheduler.jobstores.base import JobLookupError

from base.bot_init import bot
from base.scheduler_init import scheduler
from base.storage_init import storage
from config import cfg
from sessions.user_controller import send_posts_by_user
from utils.decorators import USER_FAILED
from utils.schemas import State


async def post_task(user_name: str, post_name: str):
    storage_key = StorageKey(bot_id=bot.id, user_id=cfg.ADMIN_USER_ID, chat_id=cfg.ADMIN_USER_ID)
    user_data = State(await storage.get_data(storage_key))
    job_id = f"{user_name}{post_name}"

    if user_name not in user_data.sessions:
        delete_post_task(job_id)
        return await _admin_message(f'Task was deleted, user "{user_name}" of task not found')

    user = user_data.sessions[user_name]
    if user.is_blocked:
        delete_post_task(job_id)
        return await _admin_message(f'Task was deleted, user "{user_name}" was blocked or unauthorized')

    if post_name not in user.posts:
        delete_post_task(job_id)
        return await _admin_message(f'Task was deleted, post "{post_name}" does not exist')

    post = user.posts[post_name]
    if len(user.chats) == 0:
        delete_post_task(job_id)
        return await _admin_message(f'Task was deleted, user "{user_name}" has no chats')

    if not post.create:
        user.delete_post(post_name)
        await storage.set_data(storage_key, user_data.dict())

        delete_post_task(job_id)
        return await _admin_message(f'Task was deleted, user "{user_name}" post "{post_name}" was not created')

    if await send_posts_by_user(user_name, user, post) == USER_FAILED:
        delete_post_task(job_id)
        return await _admin_message(f'Task was deleted, user "{user_name}" was blocked or unauthorized')

    post.period_time -= post.frequency_time
    if post.period_time <= 0:
        user.delete_post(post_name)
        delete_post_task(job_id)
        await _admin_message(f'Task was deleted, post "{post_name}" period is over')

    await storage.set_data(storage_key, user_data.dict())


def delete_post_task(job_id: str):
    try:
        scheduler.remove_job(job_id=job_id)
    except JobLookupError:
        pass


async def create_post_task(user_name: str, post_name: str, frequency_time: float):
    job_id = f"{user_name}{post_name}"
    delete_post_task(job_id)

    scheduler.add_job(
        post_task,
        trigger='interval',
        seconds=frequency_time,
        args=[user_name, post_name],
        id=job_id
    )


async def _admin_message(text: str):
    await bot.send_message(
        chat_id=cfg.ADMIN_USER_ID,
        text=text
    )
