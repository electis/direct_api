import json
import redis

import settings


class RedisDB(object):

    def __init__(self, db, delimiter='.'):
        self.db = redis.Redis(db=db)
        self.delimiter = delimiter

    def set(self, name, value):
        return self.db.set(name, value)

    def get(self, name, default=None):
        result = self.db.get(name)
        if result is None:
            return default
        return result

    def hset(self, name, key, value):
        return self.db.hset(name, key, value)

    def hget(self, name, key):
        return self.db.hget(name, key)

    def jset(self, name, key, value):
        return self.db.hset(name, key, json.dumps(value))

    def jget(self, name, key, default=None):
        result = self.db.hget(name, key)
        if result is None:
            return default
        return json.loads(result)

    def mset(self, name, subname, key, value):
        return self.db.hset(name, f'{subname}{self.delimiter}{key}', value)

    def mget(self, name, subname, key):
        return self.db.hget(name, f'{subname}{self.delimiter}{key}')

    def delete(self, name):
        self.db.delete(name)


cache = RedisDB(settings.REDIS_DB)
