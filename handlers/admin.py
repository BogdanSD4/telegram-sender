from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from sessions.utils import delete_session
from utils.keyboards import user_keyboard, authorization_menu_keyboard
from utils.schemas import State
from utils.states import AuthStates

router = Router()


@router.callback_query(F.data == 'main_admin')
async def admin_callback_query(query: CallbackQuery, state: FSMContext):
    data = State(await state.get_data())

    user_info = data.selected_user.info
    text = (f"ID: {user_info.user_id}\n"
            f"Name: {user_info.name}\n"
            f"Username: {user_info.username}")

    return await query.message.answer(
        text=text,
        reply_markup=user_keyboard()
    )


@router.callback_query(F.data == 'admin_delete_user')
async def exit_callback_query(query: CallbackQuery, state: FSMContext):
    data = State(await state.get_data())

    delete_session(data.selected_user_name)
    data.delete_session(data.selected_user_name)
    data.selected_user_name = None
    await query.message.answer(f"Log in:", reply_markup=authorization_menu_keyboard(data))

    await state.set_data(data.dict())


@router.callback_query(F.data == 'admin_change_user')
async def exit_callback_query(query: CallbackQuery, state: FSMContext):
    data = State(await state.get_data())

    data.selected_user_name = None
    await query.message.answer(f"Log in:", reply_markup=authorization_menu_keyboard(data))

    await state.set_data(data.dict())


@router.callback_query(F.data == 'admin_reauthorize_user')
async def reauthorize_callback_query(query: CallbackQuery, state: FSMContext):
    data = State(await state.get_data())

    data.auth.name = data.selected_user_name
    await state.set_data(data.dict())

    await state.set_state(AuthStates.wait_phone)
    await query.message.answer(
        text='Ok, send me user phone like this: 380...'
    )