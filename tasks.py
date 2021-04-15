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
    # tmpfilename = d['tmpfilename'].split('.')
    filename = d['filename'].split('.')
    y_id = filename[1]
    format = filename[2]
    if d['status'] == 'error':
        cache.sset(y_id, format, 'error', 'DownloadError')
    elif d['status'] == 'downloading':
        status = int(float(d.get('_percent_str', '0').strip('%')))
        cache.sset(y_id, format, 'status', status)
    elif d['status'] == 'finished':
        cache.sset(y_id, format, 'status', 100)
        cache.sset(y_id, format, 'filename', d['filename'])


def youtube_download(y_id, format):
    status = cache.sget(y_id, format, 'status')
    if status:
        print('Already running?')
        return

    cache.sset(y_id, format, 'status', 0)
    filename = f"{y_id}.{format}"
    url = f'http://www.youtube.com/watch?v={y_id}'
    ydl_opts = {
        # 'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'ExecAfterDownload',
            'exec_cmd': 'mv {} ' + f'{filename}.mp4'
        }],
        'format': f'{format}+bestaudio',
        'outtmpl': f'tmp.{filename}',
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        'merge_output_format': 'mp4'
    }
    os.chdir(settings.DOWNLOAD_PATH)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ret_code = ydl.download([url])
        except youtube_dl.utils.DownloadError:
            cache.sset(y_id, format, 'error', 'DownloadError')
            raise
