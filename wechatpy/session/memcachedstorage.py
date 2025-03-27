# -*- coding: utf-8 -*-
import json

from wechatpy.session import SessionStorage
from wechatpy.utils import to_text


class MemcachedStorage(SessionStorage):
    def __init__(self, mc, prefix="wechatpy"):
        for method_name in ("get", "set", "delete"):
            assert hasattr(mc, method_name)
        self.mc = mc
        self.prefix = prefix

    def key_name(self, key):
        return f"{self.prefix}:{key}"

    async def get(self, key, default=None):
        key = self.key_name(key)
        value = await self.mc.get(key)
        if value is None:
            return default
        return json.loads(to_text(value))

    async def set(self, key, value, ttl=0):
        if value is None:
            return
        key = self.key_name(key)
        value = json.dumps(value)
        await self.mc.set(key, value, ttl)

    async def delete(self, key):
        key = self.key_name(key)
        await self.mc.delete(key)
