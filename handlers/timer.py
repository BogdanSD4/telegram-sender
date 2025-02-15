import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup

from utils.keyboards import select_time_keyboard, main_menu_keyboard
from utils.states import PostStats


router = Router()


def get_time(data: dict):
    return (f"Year: {data['year']} "
            f"Month: {data['month']} "
            f"Day: {data['day']} "
            f"Hour: {data['hour']} "
            f"Minute: {data['minute']}")


@router.callback_query(F.data.startswith('next_'))
async def next_time(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if 'time_data' not in data:
        data['time_data'] = {
            'year': 0,
            'month': 0,
            'day': 0,
            'hour': 0,
            'minute': 0
        }

    if 'selected_post' in data:
        time = query.data.replace('next_', '')
        time_data = data['time_data']
        time_data[time] += 1

        await query.bot.edit_message_text(
            chat_id=query.from_user.id,
            message_id=query.message.message_id,
            text=get_time(time_data),
            reply_markup=select_time_keyboard()
        )

        await state.set_data(data)


@router.callback_query(F.data.startswith('previous_'))
async def previous_time(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if 'time_data' not in data:
        data['time_data'] = {
            'year': 0,
            'month': 0,
            'day': 0,
            'hour': 0,
            'minute': 0
        }

    if 'selected_post' in data:
        time = query.data.replace('previous_', '')
        time_data = data['time_data']
        if time_data[time] > 0:
            time_data[time] -= 1

            await query.bot.edit_message_text(
                chat_id=query.from_user.id,
                message_id=query.message.message_id,
                text=get_time(time_data),
                reply_markup=select_time_keyboard()
            )

        await state.set_data(data)


@router.callback_query(F.data == 'save_time')
async def save_time(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    state_data = await state.get_state()

    if 'selected_post' in data and 'time_data' in data:
        post = data['posts'][data['selected_post']]

        if state_data == PostStats.post_period:
            post_period = post['period']
            for key, value in data['time_data'].items():
                post_period[key] = value

            await query.bot.delete_message(
                chat_id=query.from_user.id,
                message_id=query.message.message_id
            )

            await query.message.answer(text=f"Post period has been saved")
            await query.message.answer(text='Select the frequency of sending posts')
            await query.message.answer(
                text=get_time(post['frequency']),
                reply_markup=select_time_keyboard()
            )

            del data['time_data']
            await state.set_state(PostStats.post_frequency)

        elif state_data == PostStats.post_frequency:
            post_frequency = post['frequency']
            for key, value in data['time_data'].items():
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

            del data['time_data']
            del data['selected_post']
            await state.set_state(None)

        await state.set_data(data)
