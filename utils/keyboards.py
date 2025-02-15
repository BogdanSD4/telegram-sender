from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard():
    keywords = [
        [InlineKeyboardButton(text='Create post', callback_data='main_create_post')],
        [InlineKeyboardButton(text='Your post', callback_data='main_posts')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keywords)


def select_time_keyboard():
    keywords = [
        [
            InlineKeyboardButton(text='▲', callback_data='next_year'),
            InlineKeyboardButton(text='▲', callback_data='next_month'),
            InlineKeyboardButton(text='▲', callback_data='next_day'),
            InlineKeyboardButton(text='▲', callback_data='next_hour'),
            InlineKeyboardButton(text='▲', callback_data='next_minute'),
        ],
        [
            InlineKeyboardButton(text='Year', callback_data='year'),
            InlineKeyboardButton(text='Month', callback_data='month'),
            InlineKeyboardButton(text='Day', callback_data='day'),
            InlineKeyboardButton(text='Hour', callback_data='hour'),
            InlineKeyboardButton(text='Minute', callback_data='minute'),
        ],
        [
            InlineKeyboardButton(text='▼', callback_data='previous_year'),
            InlineKeyboardButton(text='▼', callback_data='previous_month'),
            InlineKeyboardButton(text='▼', callback_data='previous_day'),
            InlineKeyboardButton(text='▼', callback_data='previous_hour'),
            InlineKeyboardButton(text='▼', callback_data='previous_minute'),
        ],
        [InlineKeyboardButton(text='Save', callback_data=f'save_time')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keywords)
