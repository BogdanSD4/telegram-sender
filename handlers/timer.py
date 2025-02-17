import logging
from datetime import timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup

from scheduler.posts import create_post_task
from utils.keyboards import select_time_keyboard, main_menu_keyboard
from utils.states import PostStats


router = Router()


def get_time(data: dict):
    return (f"Year: {data['year']}\n"
            f"Month: {data['month']}\n"
            f"Day: {data['day']}\n"
            f"Hour: {data['hour']}\n"
            f"Minute: {data['minute']}")


def create_time_data(data: dict, new: bool = False):
    if 'time_data' not in data or new:
        data['time_data'] = {
            'year': 0,
            'month': 0,
            'day': 0,
            'hour': 0,
            'minute': 0,
            'amount': 1
        }


def get_seconds_from_time_data(data: dict):
    days = data['year'] * 365 + data['month'] * 30 + data['day']
    interval = timedelta(days=days, hours=data['hour'], minutes=data['minute'])
    return interval.total_seconds()


@router.callback_query(F.data.startswith('amount_'))
async def amount_callback(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    create_time_data(data)

    event = query.data.replace('amount_', '')

    time_data = data['time_data']
    if event == 'next':
        time_data['amount'] += 1
    elif event == 'previous' and time_data['amount'] > 1:
        time_data['amount'] -= 1

    await query.bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        text=get_time(time_data),
        reply_markup=select_time_keyboard(time_data['amount'])
    )

    await state.set_data(data)


@router.callback_query(F.data.startswith('next_'))
async def next_time(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    create_time_data(data)

    if 'selected_post' in data:
        time = query.data.replace('next_', '')
        time_data = data['time_data']
        time_data[time] += time_data['amount']

        await query.bot.edit_message_text(
            chat_id=query.from_user.id,
            message_id=query.message.message_id,
            text=get_time(time_data),
            reply_markup=select_time_keyboard(time_data['amount'])
        )

        await state.set_data(data)


@router.callback_query(F.data.startswith('previous_'))
async def previous_time(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    create_time_data(data)

    if 'selected_post' in data:
        time = query.data.replace('previous_', '')
        time_data = data['time_data']
        if time_data[time] > 0:
            time_data[time] -= time_data['amount']
            if time_data[time] < 0:
                time_data[time] = 0

            await query.bot.edit_message_text(
                chat_id=query.from_user.id,
                message_id=query.message.message_id,
                text=get_time(time_data),
                reply_markup=select_time_keyboard(time_data['amount'])
            )

        await state.set_data(data)


@router.callback_query(F.data == 'save_time')
async def save_time(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_data = await state.get_state()

    if 'selected_post' in data and 'time_data' in data:
        post_name = data['selected_post']
        post = data['posts'][post_name]

        total_seconds = get_seconds_from_time_data(data['time_data'])
        if total_seconds == 0:
            return await query.message.answer(
                text="Time not set",
            )

        if state_data == PostStats.post_period:
            post['period_time'] = total_seconds
            post_period = post['period']

            for key, value in data['time_data'].items():
                if key in ['amount']:
                    continue
                post_period[key] = value

            await query.bot.delete_message(
                chat_id=query.from_user.id,
                message_id=query.message.message_id
            )

            await query.message.answer(text=f"Post period has been saved")
            await query.message.answer(text='Select the frequency of sending posts')

            create_time_data(data, True)
            await query.message.answer(
                text=get_time(post['frequency']),
                reply_markup=select_time_keyboard(data['time_data']['amount'])
            )

            await state.set_state(PostStats.post_frequency)

        elif state_data == PostStats.post_frequency:
            if total_seconds > post['period_time']:
                return await query.message.answer(
                    text='Post frequency cannot be more than period',
                )

            post['frequency_time'] = total_seconds
            post_frequency = post['frequency']

            for key, value in data['time_data'].items():
                if key in ['amount']:
                    continue
                post_frequency[key] = value

            await query.bot.delete_message(
                chat_id=query.from_user.id,
                message_id=query.message.message_id
            )

            await query.message.answer(text=f"Post frequency has been saved")
            await query.message.answer(
                text='Your post created successfully',
                reply_markup=main_menu_keyboard()
            )

            post['create'] = True
            await create_post_task(post_name, total_seconds)

            del data['time_data']
            del data['selected_post']
            await state.set_state(None)

        await state.set_data(data)
