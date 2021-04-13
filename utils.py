import json
from redis import Redis

import settings


class RedisDB(Redis):
    delimiter = '.'

    def jset(self, name, key, value):
        return self.hset(name, key, json.dumps(value))

    def jget(self, name, key, default=None):
        result = self.hget(name, key)
        if result is None:
            return default
        return json.loads(result)

    def sset(self, name, subname, key, value):
        return self.hset(name, f'{subname}{self.delimiter}{key}', value)

    def sget(self, name, subname, key):
        return self.hget(name, f'{subname}{self.delimiter}{key}')


cache = RedisDB.from_url(settings.REDIS)
