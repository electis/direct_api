'''
Бэкграунд таски
'''
import os

from youtube_dl import YoutubeDL, utils

from . import settings
from .utils import cache


class MyLogger:
    '''
    Логгер процесса скачивания
    '''
    def debug(self, msg):
        '''
        дебаг сообщения, в основном прогресс скачивания
        '''
        # print('debug', msg)
        pass

    def warning(self, msg):
        print('warning', msg)

    def error(self, msg):
        print('error', msg)


def my_hook(d):
    '''
    Вызывается постоянно в процессе скачивания,
    используется для сохранения прогресса в базе
    '''
    # tmpfilename = d['tmpfilename'].split('.')
    filename = d['filename'].split('.')
    y_id = filename[1]
    v_format = filename[2]
    if d['status'] == 'error':
        cache.sset(y_id, v_format, 'error', 'DownloadError')
    elif d['status'] == 'downloading':
        status = int(float(d.get('_percent_str', '0').strip('%')))
        cache.sset(y_id, v_format, 'status', status)
    elif d['status'] == 'finished':
        cache.sset(y_id, v_format, 'status', 100)
        cache.sset(y_id, v_format, 'filename', d['filename'])


def youtube_download(y_id, v_format):
    '''
    Фоновая задача скачивания с ютуба,
    по окончанию скачивания переименовывает файл в прописаный формат
    '''
    status = cache.sget(y_id, v_format, 'status')
    if status:
        print('Already running?')
        return

    cache.sset(y_id, v_format, 'status', 0)
    filename = f"{y_id}.{v_format}"
    url = f'http://www.youtube.com/watch?v={y_id}'
    ydl_opts = {
        # 'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'ExecAfterDownload',
            'exec_cmd': 'mv {} ' + f'{filename}.mp4'
        }],
        'format': f'{v_format}+bestaudio',
        'outtmpl': f'tmp.{filename}',
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        'merge_output_format': 'mp4'
    }
    os.chdir(settings.DOWNLOAD_PATH)
    with YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except utils.DownloadError:
            cache.sset(y_id, format, 'error', 'DownloadError')
            raise
