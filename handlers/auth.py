import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from scheduler.posts import create_post_task
from sessions.schemas import SessionRequest
from sessions.session_manager import auth_get_hash, auth_create_session, get_user_info
from sessions.user_controller import get_user_chats
from utils.keyboards import main_menu_keyboard, users_menu_keyboard, blocked_user_keyboard
from utils.schemas import State, StateSession
from utils.states import AuthStates

router = Router()


@router.callback_query(F.data == 'main_auth')
async def auth_callback_query(query: CallbackQuery, state: FSMContext):
    await state.set_state(AuthStates.wait_auth_name)
    await query.message.answer(
        text='Send me username'
    )


@router.message(AuthStates.wait_auth_name)
async def wait_auth_name(message: Message, state: FSMContext):
    data = State(await state.get_data())
    data.auth.name = message.text
    await state.set_data(data.dict())

    await state.set_state(AuthStates.wait_phone)
    await message.answer(
        text='Ok, send me user phone like this: 380...'
    )


@router.message(AuthStates.wait_phone)
async def wait_phone(message: Message, state: FSMContext):
    data = State(await state.get_data())

    if not message.text.startswith('380'):
        return await message.answer(
            text='No, phone must start with "380"'
        )

    data.auth.phone = message.text
    await state.set_data(data.dict())

    await state.set_state(AuthStates.wait_password)
    await message.answer(
        text='Ok, send me user password'
    )


@router.message(AuthStates.wait_password)
async def wait_password(message: Message, state: FSMContext):
    data = State(await state.get_data())

    data.auth.password = message.text
    await state.set_data(data.dict())

    response = await auth_get_hash(data.auth.name, SessionRequest(
        name=data.auth.name,
        phone=data.auth.phone,
        password=data.auth.password
    ))

    if not response.value:
        return await message.answer(
            text=f'Something wrong: {response.error}, please try again'
        )

    data.auth.code_hash = response.value
    await state.set_data(data.dict())

    await state.set_state(AuthStates.wait_code)
    await message.answer(
        text='Ok, send me telegram auth code like this: __code'
    )


@router.message(AuthStates.wait_code)
async def wait_code(message: Message, state: FSMContext):
    data = State(await state.get_data())

    if not message.text.startswith('__'):
        return await message.answer(
            text='No, code must start with "__"'
        )

    try:
        code = int(message.text.replace('__', ''))
    except ValueError:
        return await message.answer(
            text='Invalid code, please try again'
        )

    response = await auth_create_session(data.auth.name, SessionRequest(
        name=data.auth.name,
        phone=data.auth.phone,
        password=data.auth.password,
        code_hash=data.auth.code_hash,
        code=code
    ))

    if not response.value:
        return await message.answer(
            text=f'Something wrong: {response.error}, please try again'
        )

    session = StateSession()
    session.info = await get_user_info(data.auth.name)
    logging.info(f"User info: {session.info}")
    session.chats = await get_user_chats(data.auth.name)
    data.add_session(data.auth.name, session)

    # Create job if user have posts
    for post_name, post in session.posts.items():
        await create_post_task(data.auth.name, post_name, post.frequency_time)

    data.clear_auth()
    await state.set_data(data.dict())
    await state.set_state(None)

    await message.answer(
        text=response.value,
        reply_markup=users_menu_keyboard(data)
    )


@router.callback_query(F.data.startswith('main_enter&'))
async def main_enter(query: CallbackQuery, state: FSMContext):
    data = State(await state.get_data())
    username = query.data.replace('main_enter&', '')

    data.selected_user_name = username
    await state.set_data(data.dict())

    if data.selected_user.is_blocked:
        return await query.message.answer(
            text=f'This user is blocked or unauthorized',
            reply_markup=blocked_user_keyboard()
        )

    await query.message.answer(
        text=f'Main menu {username}',
        reply_markup=main_menu_keyboard()
    )


