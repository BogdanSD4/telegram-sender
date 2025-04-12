from aiogram.fsm.state import StatesGroup, State


class PostStats(StatesGroup):
    wait_post_name = State()
    wait_post = State()
    post_period = State()
    post_frequency = State()


class AuthStates(StatesGroup):
    wait_auth_name = State()
    wait_phone = State()
    wait_password = State()
    wait_code = State()