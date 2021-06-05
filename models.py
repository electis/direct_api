import json

import youtube_dl
from redis import Redis

import settings


class RedisDB(Redis):
    delimiter: str = None
    prefix: str = None

    def __init__(self, *args, delimiter=settings.REDIS_DELIMITER, prefix='', **kwargs):
        self.set_attrib(delimiter, prefix)
        super().__init__(*args, **kwargs)

    @classmethod
    def from_url(cls, url, db=None, delimiter=settings.REDIS_DELIMITER, prefix='', **kwargs):
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
        value = self.hget(self.make_name(name), self.make_key(subname, key))
        if isinstance(value, bytes):
            return value.decode()
        return value

    def sdel(self, name, subname, key):
        return self.hdel(self.make_name(name), self.make_key(subname, key))

    def del_one(self, name):
        self.delete(self.make_name(name))


cache = RedisDB.from_url(settings.REDIS, prefix='youtube')


class YouTube:
    url_format = 'http://www.youtube.com/watch?v={}'
    filename = '{y_id}' + settings.FILE_DELIMITER + '{format}'

    @classmethod
    async def extract_info(cls, y_id):
        with youtube_dl.YoutubeDL() as ydl:
            video = ydl.extract_info(cls.url_format.format(y_id), download=False)
            # except youtube_dl.utils.DownloadError:
        # Can be a playlist or a list of videos
        if 'entries' in video:
            video = video['entries'][0]
        cache.jset(y_id, 'info', video)
        return video
