import json
import os

import youtube_dl
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

    def sdel(self, name, subname, key):
        return self.hdel(self.make_name(name), self.make_key(subname, key))

    def del_one(self, name):
        self.delete(self.make_name(name))


cache = RedisDB.from_url(settings.REDIS, prefix='youtube')


class YouTube:
    y_id: str = None
    video: dict = None
    _url_format = 'http://www.youtube.com/watch?v={y_id}'
    _url: str = None

    def __init__(self, y_id):
        self.y_id = y_id
        self._url = self._url_format.format(y_id=y_id)
        self.video = cache.jget(self.y_id, 'info')

    def extract_info(self):
        if not self.video:
            with youtube_dl.YoutubeDL() as ydl:
                video = ydl.extract_info(self._url, download=False)
                # except youtube_dl.utils.DownloadError:
            if 'entries' in video:
                video = video['entries'][0]  # Can be a playlist or a list of videos
            cache.jset(self.y_id, 'info', video)
            self.video = video
        return self

    def clear(self):
        ...
        filename = f"{self.y_id}_{format}"
        os.remove(filename)
        cache.del_one(self.y_id)
