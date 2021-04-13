import os

import youtube_dl

import settings
from utils import cache


class MyLogger(object):
    def debug(self, msg):
        # print('debug', msg)
        pass

    def warning(self, msg):
        print('warning', msg)

    def error(self, msg):
        print('error', msg)


def my_hook(d):
    y_id = ...
    format = ...
    name = f'youtube_{y_id}'
    if d['status'] == 'error':
        cache.sset(name, format, 'error', 'DownloadError')
    elif d['status'] == 'downloading':
        status = int(float(d.get('_percent_str', '0').strip('%')))
        cache.sset(name, format, 'status', status)
    elif d['status'] == 'finished':
        cache.sset(name, format, 'status', 100)
        cache.sset(name, format, 'filename', ...)


def youtube_download(y_id, format, name):
    filename = f"{y_id}_{format}"
    status = cache.sget(name, format, 'status')
    if status:
        print('Already running?')
        return

    cache.mset(name, format, 'status', 0)
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
        # 'output': f'{filename}.%(ext)s',
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        'merge_output_format': 'mp4'
    }
    os.chdir(settings.DOWNLOAD_PATH)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except youtube_dl.utils.DownloadError:
            cache.sset(name, format, 'error', 'DownloadError')
            raise
