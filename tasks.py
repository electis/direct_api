import os

import redis
import youtube_dl
# from celery import Celery

import settings

redis_con = redis.Redis(db=settings.REDIS_DB)


class MyLogger(object):
    def debug(self, msg):
        # print('debug', msg)
        pass

    def warning(self, msg):
        print('warning', msg)

    def error(self, msg):
        print('error', msg)


def my_hook(d):
    filename = d['filename'].split('.')[0]
    redis_name = f'youtube_download_{filename}'
    if d['status'] == 'error':
        redis_con.set(redis_name, 'download error')
    elif d['status'] == 'downloading':
        redis_con.set(redis_name, d.get('_percent_str', '0').strip())
    elif d['status'] == 'finished':
        redis_con.set(redis_name, 100)


def youtube_download(y_id, format):
    filename = f"{y_id}_{format}"
    redis_name = f'youtube_download_{filename}'
    status = redis_con.get(redis_name)
    if status:
        # check for task?
        return

    redis_con.set(redis_name, 0)
    url = f'http://www.youtube.com/watch?v={y_id}'
    ydl_opts = {
        # 'format': 'bestaudio/best',
        # 'postprocessors': [{
        #     'key': 'FFmpegExtractAudio',
        #     'preferredcodec': 'mp3',
        #     'preferredquality': '192',
        # }],
        'format': f'{format}+bestaudio',
        'outtmpl': f'{filename}',
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }
    os.chdir(settings.DOWNLOAD_PATH)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except youtube_dl.utils.DownloadError as exc:
            raise
    redis_con.set(redis_name, 100)
