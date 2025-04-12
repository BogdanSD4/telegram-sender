from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.schemas import State


def main_menu_keyboard():
    keywords = [
        [InlineKeyboardButton(text='Create post', callback_data='main_create_post')],
        [InlineKeyboardButton(text='Your post', callback_data='main_posts')],
        [InlineKeyboardButton(text='Your chats', callback_data='main_chats')],
        [InlineKeyboardButton(text='Admin', callback_data='main_admin')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keywords)


def authorization_menu_keyboard(data: State):
    keywords = _get_user_inline_buttons(data)
    keywords.append([InlineKeyboardButton(text='Authorization', callback_data='main_auth')])
    return InlineKeyboardMarkup(inline_keyboard=keywords)


def users_menu_keyboard(data: State):
    return InlineKeyboardMarkup(inline_keyboard=_get_user_inline_buttons(data))


def _get_user_inline_buttons(data: State):
    return [
        [
            InlineKeyboardButton(
                text=f"{session}{' - blocked' if data.sessions[session].is_blocked else ''}",
                callback_data=f'main_enter&{session}'
            )
        ]for session in data.sessions.keys()
    ]


def chats_menu_keyboard(data: State):
    chats = data.selected_user.chats
    if len(chats) > 0:
        keyboard = [
            [
                InlineKeyboardButton(text=value.name, callback_data=f'none'),
                # InlineKeyboardButton(text='Delete chat', callback_data=f'delete_chat_{key}'),
            ] for key, value in chats.items()
        ]
    else:
        keyboard = [[InlineKeyboardButton(text="No chats", callback_data=f'no_posts')]]

    keyboard.append([InlineKeyboardButton(text='Reload', callback_data='reload_chats')])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def user_keyboard():
    keyboard = [
        [InlineKeyboardButton(text='Change user', callback_data=f'admin_change_user')],
        [InlineKeyboardButton(text='❌ Delete user', callback_data=f'admin_delete_user')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def blocked_user_keyboard():
    keyboard = [
        [InlineKeyboardButton(text='Reauthorize', callback_data=f'admin_reauthorize_user')],
        [InlineKeyboardButton(text='❌ Delete user', callback_data=f'admin_delete_user')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def select_time_keyboard(amount: int):
    keyboard = [
        [
            InlineKeyboardButton(text='▲', callback_data='next_year'),
            InlineKeyboardButton(text='▲', callback_data='next_month'),
            InlineKeyboardButton(text='▲', callback_data='next_day'),
            InlineKeyboardButton(text='▲', callback_data='next_hour'),
            InlineKeyboardButton(text='▲', callback_data='next_minute'),
            InlineKeyboardButton(text=' ', callback_data='none'),
            InlineKeyboardButton(text='▲', callback_data='amount_next'),
        ],
        [
            InlineKeyboardButton(text='Y', callback_data='year'),
            InlineKeyboardButton(text='M', callback_data='month'),
            InlineKeyboardButton(text='D', callback_data='day'),
            InlineKeyboardButton(text='H', callback_data='hour'),
            InlineKeyboardButton(text='Min', callback_data='minute'),
            InlineKeyboardButton(text=' ', callback_data='none'),
            InlineKeyboardButton(text=f'{amount}', callback_data='none'),
        ],
        [
            InlineKeyboardButton(text='▼', callback_data='previous_year'),
            InlineKeyboardButton(text='▼', callback_data='previous_month'),
            InlineKeyboardButton(text='▼', callback_data='previous_day'),
            InlineKeyboardButton(text='▼', callback_data='previous_hour'),
            InlineKeyboardButton(text='▼', callback_data='previous_minute'),
            InlineKeyboardButton(text=' ', callback_data='none'),
            InlineKeyboardButton(text='▼', callback_data='amount_previous'),
        ],
        [InlineKeyboardButton(text='Save', callback_data=f'save_time')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
