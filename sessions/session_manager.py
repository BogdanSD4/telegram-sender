import logging
import os
from pathlib import Path

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from config import cfg
from sessions.schemas import SessionResponse, SessionRequest
from sessions.utils import session_path
from utils.decorators import telethon_user
from utils.schemas import StateUser


@telethon_user
async def is_authorized(client: str | TelegramClient, **kwargs) -> bool:
    return await client.is_user_authorized()


@telethon_user
async def get_user_info(client: str | TelegramClient) -> StateUser | None:
    if not await is_authorized(client, no_disconnect=True):
        return None

    user = await client.get_me()

    return StateUser({
        "user_id": user.id,
        "name": f"{user.first_name} {user.last_name}",
        "username": user.username
    })


@telethon_user
async def auth_get_hash(
        client: str | TelegramClient,
        request: SessionRequest
) -> SessionResponse:
    if await is_authorized(client, no_disconnect=True):
        return SessionResponse(error='This session is already authorized')

    response = await client.send_code_request(request.phone)
    return SessionResponse(value=response.phone_code_hash)


@telethon_user
async def auth_create_session(
        client: str | TelegramClient,
        request: SessionRequest
) -> SessionResponse:
    if await is_authorized(client, no_disconnect=True):
        return SessionResponse(error='This session is already authorized')

    try:
        await client.sign_in(
            request.phone,
            request.code,
            phone_code_hash=request.code_hash
        )
    except SessionPasswordNeededError:
        if not request.password:
            return SessionResponse(error="Password is required!")
        await client.sign_in(password=request.password)

    return SessionResponse(value=f'User {request.name} authenticated successfully')

