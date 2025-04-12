import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from handlers.timer import get_time
from media.media_manager import save_media
from scheduler.posts import delete_post_task
from utils.keyboards import select_time_keyboard
from utils.schemas import State, StatePost
from utils.states import PostStats


router = Router()


@router.callback_query(F.data == "main_create_post")
async def main_post(query: CallbackQuery, state: FSMContext):
    await query.message.answer(text='Send post name')
    await state.set_state(PostStats.wait_post_name)


@router.message(PostStats.wait_post_name)
async def wait_post_name(message: Message, state: FSMContext):
    data = State(await state.get_data())

    if len(message.text) > 50:
        return await message.answer(text="This name is too long")

    if message.text in data.selected_user.posts:
        return await message.answer(text="Post with this name already exists")

    data.selected_user.selected_post_name = message.text

    await state.set_state(PostStats.wait_post)
    await state.set_data(data.dict())

    await message.answer(text=f"Create a new post with name \"{message.text}\"")
    await message.answer(text='Send post body')


@router.message(PostStats.wait_post)
async def wait_post(message: Message, state: FSMContext):
    data = State(await state.get_data())
    user = data.selected_user

    if user.selected_post_name:
        if message.voice:
            media = message.voice
        elif message.video:
            media = message.video
        elif message.audio:
            media = message.audio
        elif message.photo:
            media = message.photo[-1]
        else:
            media = None

        [media, media_type] = await save_media(media)

        user.add_post(user.selected_post_name, StatePost({
            'text': message.text,
            'caption': message.caption,
            'media': media,
            'media_type': media_type
        }))

        await message.answer(text="Your post body has been saved")
        await message.answer(text="Select the period for sending posts")

        user.time_data.reset()

        timer_message = await message.answer(
            text=get_time(user.selected_post.period.dict()),
            reply_markup=select_time_keyboard(user.time_data.amount)
        )
        user.timer_message_id = timer_message.message_id

        await state.set_state(PostStats.post_period)
        await state.set_data(data.dict())


@router.callback_query(F.data == "main_posts")
async def main_posts(query: CallbackQuery, state: FSMContext):
    data = State(await state.get_data())

    posts = {}
    if len(data.selected_user.posts) > 0:
        for key, value in data.selected_user.posts.items():
            if value.create:
                posts[key] = value.dict()
            else:
                data.selected_user.delete_post(key)

    if len(posts) > 0:
        keyword = [
            [
                InlineKeyboardButton(text=name, callback_data=f'post_{name}'),
                InlineKeyboardButton(text='Delete post', callback_data=f'delete_post_{name}')
            ]for name in posts.keys()
        ]
    else:
        keyword = [[InlineKeyboardButton(text="No posts", callback_data=f'no_posts')]]

    await query.message.answer(
        text='Your posts:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyword)
    )
    await state.set_data(data.dict())


@router.callback_query(F.data.startswith("delete_post_"))
async def delete_post(query: CallbackQuery, state: FSMContext):
    data = State(await state.get_data())
    post_name = query.data.replace('delete_post_', '')

    if post_name in data.selected_user.posts:
        data.selected_user.delete_post(post_name)

        delete_post_task(f"{data.selected_user_name}{post_name}")

        await query.message.answer(
            text=f'Post {post_name} delete successfully'
        )

    await state.set_data(data.dict())
