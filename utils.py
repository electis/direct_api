import json
from redis import Redis

import settings


class RedisDB(Redis):
    delimiter: str = None
    prefix: str = None

    def __init__(self, *args, delimiter='|', prefix='', **kwargs):
        self.set_attrib(delimiter, prefix)
        super().__init__(*args, **kwargs)

    @classmethod
    def from_url(cls, url, db=None, delimiter='|', prefix='', **kwargs):
        self = super().from_url(url, db=None, **kwargs)
        cls.set_attrib(self, delimiter, prefix)
        return self

    def set_attrib(self, delimiter, prefix):
        if self.delimiter is None:
            self.delimiter = delimiter
        if self.prefix is None:
            self.prefix = prefix

    def make_name(self, name):
        return f"{self.prefix}{self.delimiter}{name}"

    def make_key(self, subname, key):
        return f"{subname}{self.delimiter}{key}"

    def jset(self, name, key, value):
        return self.hset(self.make_name(name), key, json.dumps(value))

    def jget(self, name, key, default=None):
        result = self.hget(self.make_name(name), key)
        if result is None:
            return default
        return json.loads(result)

    def sset(self, name, subname, key, value):
        return self.hset(self.make_name(name), self.make_key(subname, key), value)

    def sget(self, name, subname, key):
        return self.hget(self.make_name(name), self.make_key(subname, key))

    def del_one(self, name):
        self.delete(self.make_name(name))


cache = RedisDB.from_url(settings.REDIS, prefix='youtube')
