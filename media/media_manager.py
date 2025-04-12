import os
from enum import Enum
from pathlib import Path

from aiogram.types import PhotoSize, Video, Audio, Voice, Message

from base.bot_init import bot


class Media(Enum):
    PHOTO = "jpg"
    VIDEO = "mp4"
    AUDIO = "mp3"
    VOICE = "mp3"


def media_path(name: str, ext: Media):
    return os.path.join(Path(__file__).parent, f"{name}.{ext.value}")


async def save_media(media: PhotoSize | Video | Audio | Voice | None) -> (str | None, Media | None):
    """
    :param media:
    :return: name, type
    """

    if not media:
        return None, None

    media_type = _get_media_type(media)

    if media_type:
        file_info = await bot.get_file(media.file_id)
        file_path = file_info.file_path

        media_name = media.file_unique_id
        destination = media_path(media_name, media_type)
        await bot.download_file(file_path, destination)

        return media_name, media_type

    raise ValueError(f"Invalid media type: {media_type}, media: {media}")


def _get_media_type(media: PhotoSize | Video | Audio | Voice) -> Media | None:
    if isinstance(media, PhotoSize):
        return Media.PHOTO
    elif isinstance(media, Video):
        return Media.VIDEO
    elif isinstance(media, Audio):
        return Media.AUDIO
    elif isinstance(media, Voice):
        return Media.VOICE

    return None


def delete_media(name: str, ext: Media):
    path = media_path(name, ext)
    if os.path.exists(path):
        os.remove(path)
