# -*- coding: utf-8 -*-


class SessionStorage:
    async def get(self, key, default=None):
        raise NotImplementedError()

    async def set(self, key, value, ttl=None):
        raise NotImplementedError()

    async def delete(self, key):
        raise NotImplementedError()

    def __getitem__(self, key):
        self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        self.delete(key)
