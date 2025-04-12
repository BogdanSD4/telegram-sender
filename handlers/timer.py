import logging
from datetime import timedelta

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup

from scheduler.posts import create_post_task
from utils.keyboards import select_time_keyboard, main_menu_keyboard
from utils.schemas import State
from utils.states import PostStats


router = Router()


def get_time(data: dict):
    return (f"Year: {data['year']}\n"
            f"Month: {data['month']}\n"
            f"Day: {data['day']}\n"
            f"Hour: {data['hour']}\n"
            f"Minute: {data['minute']}")


def get_seconds_from_time_data(data: dict):
    days = data['year'] * 365 + data['month'] * 30 + data['day']
    interval = timedelta(days=days, hours=data['hour'], minutes=data['minute'])
    logging.info(interval.total_seconds())
    return interval.total_seconds()


@router.callback_query(F.data.startswith('amount_'))
async def amount_callback(query: CallbackQuery, state: FSMContext):
    data = State(await state.get_data())

    event = query.data.replace('amount_', '')

    time_data = data.selected_user.time_data
    if event == 'next':
        time_data.amount += 1
    elif event == 'previous' and time_data.amount > 1:
        time_data.amount -= 1

    await query.bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        text=get_time(time_data.dict()),
        reply_markup=select_time_keyboard(time_data.amount)
    )

    await state.set_data(data.dict())


@router.callback_query(F.data.startswith('next_'))
async def next_time(query: CallbackQuery, state: FSMContext):
    data = State(await state.get_data())

    post = data.selected_user.selected_post
    if post:
        time = query.data.replace('next_', '')
        time_data = data.selected_user.time_data
        time_data.sum(time, time_data.amount)

        try:
            await query.bot.edit_message_text(
                chat_id=query.from_user.id,
                message_id=query.message.message_id,
                text=get_time(time_data.dict()),
                reply_markup=select_time_keyboard(time_data.amount)
            )
        except TelegramBadRequest:
            pass

        await state.set_data(data.dict())


@router.callback_query(F.data.startswith('previous_'))
async def previous_time(query: CallbackQuery, state: FSMContext):
    data = State(await state.get_data())

    post = data.selected_user.selected_post
    if post:
        time = query.data.replace('previous_', '')
        time_data = data.selected_user.time_data
        time_data.sum(time, -time_data.amount)

        try:
            await query.bot.edit_message_text(
                chat_id=query.from_user.id,
                message_id=query.message.message_id,
                text=get_time(time_data.dict()),
                reply_markup=select_time_keyboard(time_data.amount)
            )
        except TelegramBadRequest:
            pass

        await state.set_data(data.dict())


@router.callback_query(F.data == 'save_time')
async def save_time(query: CallbackQuery, state: FSMContext):
    data = State(await state.get_data())
    state_data = await state.get_state()

    post = data.selected_user.selected_post
    time_data = data.selected_user.time_data

    if post and time_data:
        total_seconds = get_seconds_from_time_data(time_data.dict())
        if total_seconds == 0:
            return await query.message.answer(
                text="Time not set",
            )

        if state_data == PostStats.post_period:
            post.period_time = total_seconds
            post.period.update(time_data.dict())

            await query.bot.delete_message(
                chat_id=query.from_user.id,
                message_id=query.message.message_id
            )

            await query.message.answer(text=f"Post period has been saved")
            await query.message.answer(text='Select the frequency of sending posts')
            await state.set_state(PostStats.post_frequency)

            time_data.reset()
            await query.message.answer(
                text=get_time(post.frequency.dict()),
                reply_markup=select_time_keyboard(time_data.amount)
            )

        elif state_data == PostStats.post_frequency:
            logging.info(f"Period time: {post.period_time}")
            if total_seconds > post.period_time:
                return await query.message.answer(
                    text='Post frequency cannot be more than period',
                )

            post.frequency_time = total_seconds
            post.frequency.update(time_data.dict())

            await query.bot.delete_message(
                chat_id=query.from_user.id,
                message_id=query.message.message_id
            )

            await query.message.answer(text=f"Post frequency has been saved")
            await query.message.answer(
                text='Your post created successfully',
                reply_markup=main_menu_keyboard()
            )

            post.create = True
            await create_post_task(data.selected_user_name, data.selected_user.selected_post_name, total_seconds)

            data.selected_user.selected_post_name = None
            await state.set_state(None)

    logging.info(f"Save: {data.dict()}")
    await state.set_data(data.dict())
