from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from handlers.timer import get_time
from utils.keyboards import select_time_keyboard
from utils.states import PostStats


router = Router()


@router.callback_query(F.data == "main_create_post")
async def main_post(query: CallbackQuery, state: FSMContext):
    await query.message.answer(text='Send post name')
    await state.set_state(PostStats.wait_post_name)


@router.message(PostStats.wait_post_name)
async def wait_post_name(message: Message, state: FSMContext):
    data = await state.get_data()

    if len(message.text) > 50:
        return await message.answer(text="This name is too long")

    if 'posts' not in data:
        data['posts'] = {}

    if message.text in data['posts']:
        return await message.answer(text="Post with this name already exists")

    data['selected_post'] = message.text

    await message.answer(text=f"Create a new post with name \"{message.text}\"")
    await message.answer(text='Send post body')

    await state.set_state(PostStats.wait_post)
    await state.set_data(data)


@router.message(PostStats.wait_post)
async def wait_post(message: Message, state: FSMContext):
    data = await state.get_data()

    if 'selected_post' in data:
        if data['selected_post'] in data:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=message.message_id
            )

        message_name = data['selected_post']
        data['posts'][message_name] = {
            'text': message.text,
            'period': {
                'year': 0,
                'month': 0,
                'day': 0,
                'hour': 0,
                'minute': 0
            },
            'frequency': {
                'year': 0,
                'month': 0,
                'day': 0,
                'hour': 0,
                'minute': 0
            },
        }

        post = data['posts'][message_name]

        await message.answer(text="Your post body has been saved")
        await message.answer(text="Select the period for sending posts")

        timer_message = await message.answer(
            text=get_time(post['period']),
            reply_markup=select_time_keyboard()
        )
        data['timer_message_id'] = timer_message.message_id

        await state.set_state(PostStats.post_period)
        await state.set_data(data)


@router.callback_query(F.data == "main_posts")
async def main_posts(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if 'posts' in data:
        keyword = [
            [InlineKeyboardButton(text=name, callback_data=f'post_{name}')]
            for name in data['posts'].keys()
        ]
    else:
        keyword = [[InlineKeyboardButton(text="No posts", callback_data=f'no_posts')]]

    await query.message.answer(
        text='Your posts:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyword)
    )
