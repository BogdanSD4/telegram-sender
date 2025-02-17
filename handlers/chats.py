import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import ChatMemberUpdated, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from base.storage_init import storage
from config import cfg
from base.bot_init import bot

router = Router()


@router.my_chat_member()
async def my_chat_member_handler(update: ChatMemberUpdated, state: FSMContext):
    logging.info('dfg')
    storage_key = StorageKey(bot_id=bot.id, user_id=cfg.ADMIN_USER_ID, chat_id=cfg.ADMIN_USER_ID)
    user_data = await storage.get_data(storage_key)

    if 'chats' not in user_data:
        user_data['chats'] = {}

    if update.new_chat_member.status in ["member", "administrator"]:
        if update.new_chat_member.status == "administrator":
            user_data['chats'][update.chat.id] = {'name': update.chat.title}

            await bot.send_message(
                chat_id=cfg.ADMIN_USER_ID,
                text=f'{update.chat.title} saved successfully!'
            )

        elif update.new_chat_member.status == "member":
            await bot.leave_chat(chat_id=update.chat.id)
            await bot.send_message(
                chat_id=cfg.ADMIN_CHAT_ID,
                text=f'Failed add bot to {update.chat.title}\nBot must be admin'
            )

    elif update.new_chat_member.status == "kicked":
        if update.chat.id in user_data['chats']:
            del user_data['chats'][update.chat.id]

        await bot.send_message(
            chat_id=cfg.ADMIN_USER_ID,
            text=f'Bot has been deleted from chat {update.chat.title}'
        )

    await storage.set_data(storage_key, user_data)


@router.callback_query(F.data == 'main_chats')
async def get_chats(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if 'chats' in data and len(data['chats']) > 0:
        keyword = [
            [
                InlineKeyboardButton(text=value['name'], callback_data=f'none'),
                InlineKeyboardButton(text='Delete chat', callback_data=f'delete_chat_{key}'),
            ] for key, value in data['chats'].items()
        ]
    else:
        keyword = [[InlineKeyboardButton(text="No chats", callback_data=f'no_posts')]]

    await query.message.answer(
        text='Your chats:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyword)
    )


@router.callback_query(F.data.startswith('delete_chat_'))
async def delete_chat(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if 'chats' not in data or len(data['chats']) == 0:
        return

    chat_id = query.data.replace('delete_chat_', '')
    title = data['chats'][chat_id]['name']

    del data['chats'][chat_id]
    await bot.leave_chat(chat_id=chat_id)
    await bot.send_message(
        chat_id=cfg.ADMIN_USER_ID,
        text=f'Bot has been deleted from chat {title}'
    )

    await state.set_data(data)
