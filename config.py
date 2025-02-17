import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    ADMIN_USER_ID = int(os.environ.get('ADMIN_USER_ID', 0))
    BOT_TOKEN = os.environ.get('BOT_TOKEN', None)
    REDIS_HOST = os.environ.get('REDIS_HOST', None)
    REDIS_PORT = int(os.environ.get('REDIS_PORT', None))


cfg = Settings()
