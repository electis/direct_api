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
    tmpfilename = d['tmpfilename'].split('.')
    format = tmpfilename[3]
    name = '.'.join(tmpfilename[1:3])
    if d['status'] == 'error':
        cache.sset(name, format, 'error', 'DownloadError')
    elif d['status'] == 'downloading':
        status = int(float(d.get('_percent_str', '0').strip('%')))
        cache.sset(name, format, 'status', status)
    elif d['status'] == 'finished':
        cache.sset(name, format, 'status', 100)
        cache.sset(name, format, 'filename', d['filename'])


def youtube_download(y_id, format, name):
    # filename = f"{y_id}_{format}"
    status = cache.sget(name, format, 'status')
    if status:
        print('Already running?')
        return

    cache.sset(name, format, 'status', 0)
    url = f'http://www.youtube.com/watch?v={y_id}'
    ydl_opts = {
        # 'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'ExecAfterDownload',
            'exec_cmd': 'mv {} ' + f'{name}.{format}.mp4'
        }],
        'format': f'{format}+bestaudio',
        'outtmpl': f'tmp.{name}.{format}',
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        'merge_output_format': 'mp4',
        'test': 'test'
    }
    os.chdir(settings.DOWNLOAD_PATH)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except youtube_dl.utils.DownloadError:
            cache.sset(name, format, 'error', 'DownloadError')
            raise
