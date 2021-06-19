"""Классы для работы с внешними данными"""
import json
from typing import Optional

import youtube_dl
from redis import Redis

import settings

from threading import Lock


class SingletonMeta(type):
    """
    потокобезопасная реализация класса Singleton.
    """
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class DB(metaclass=SingletonMeta):
    """Дополнительные методы для работы с данными в Redis"""

    def __init__(self):
        self.db = Redis.from_url(settings.REDIS)
        self.delimiter = settings.REDIS_DELIMITER

    def make_key(self, subname, key):
        """добавляет подназвание к ключу"""
        return f"{subname}{self.delimiter}{key}"

    def jset(self, name, key, value):
        """сохраняет значение как json строку"""
        return self.db.hset(name, key, json.dumps(value))

    def jget(self, name, key, default=None):
        """возвращает сохранённую json строку как объект"""
        result = self.db.hget(name, key)
        if result is None:
            return default
        return json.loads(result)

    def sset(self, name, subname, key, value):
        """сохраняет значение как строку с поддержкой подназвания"""
        return self.db.hset(name, self.make_key(subname, key), value)

    def sget(self, name, subname, key):
        """возвращает строку с поддержкой подназвания"""
        value = self.db.hget(name, self.make_key(subname, key))
        if isinstance(value, bytes):
            return value.decode()
        return value

    def scan(self, match='*'):
        return self.db.scan_iter(match)

    def delete(self, name):
        """удаляет запись по названию"""
        return self.db.delete(name)


class YouTube:
    """Получение данных с YouTube"""

    url_format = 'http://www.youtube.com/watch?v={}'
    filename = '{y_id}' + settings.FILE_DELIMITER + '{format}'

    @classmethod
    async def extract_info(cls, y_id):
        """получает данные о видео с YouTube"""
        with youtube_dl.YoutubeDL() as ydl:
            video = ydl.extract_info(cls.url_format.format(y_id), download=False)
            # except youtube_dl.utils.DownloadError:
        # Can be a playlist or a list of videos
        if 'entries' in video:
            video = video['entries'][0]
        DB().jset(y_id, 'info', video)
        return video
