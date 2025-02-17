import redis
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage

from config import cfg

redis_client = redis.asyncio.Redis(host=cfg.REDIS_HOST, port=cfg.REDIS_PORT, decode_responses=True)
storage = RedisStorage(redis=redis_client, key_builder=DefaultKeyBuilder(with_bot_id=True))
