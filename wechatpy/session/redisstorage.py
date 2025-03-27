# -*- coding: utf-8 -*-
import json

from redis.asyncio import Redis

from wechatpy.session import SessionStorage
from wechatpy.utils import to_text


class RedisStorage(SessionStorage):
    def __init__(self, redis: Redis, prefix="wechatpy"):
        for method_name in ("get", "set", "delete"):
            assert hasattr(redis, method_name)
        self.redis: Redis = redis
        self.prefix = prefix

    def key_name(self, key):
        return f"{self.prefix}:{key}"

    async def get(self, key, default=None):
        key = self.key_name(key)
        value = await self.redis.get(key)
        if value is None:
            return default
        return json.loads(to_text(value))

    async def set(self, key, value, ttl=None):
        if value is None:
            return
        key = self.key_name(key)
        value = json.dumps(value)
        await self.redis.set(key, value, ex=ttl)

    async def delete(self, key):
        key = self.key_name(key)
        await self.redis.delete(key)
