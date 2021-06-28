"""фоновые таски FastAPI"""
import os

import youtube_dl

from helpers import yt_dl_hook
import settings
from models import DB, YouTube


def youtube_download_task(y_id, video_format):
    """таск скачивания видео"""
    dbase = DB()
    status = dbase.sget(y_id, video_format, 'status')
    if status:
        print('Already running?')
        return

    dbase.sset(y_id, video_format, 'status', 0)
    filename = YouTube.filename.format(y_id=y_id, format=video_format)
    url = YouTube.url_format.format(y_id)
    ydl_opts = {
        'postprocessors': [
            {
                'key': 'ExecAfterDownload',
                # TODO can be mkv
                'exec_cmd': 'mv {} ' + f'{filename}.mp4',
            }
        ],
        'format': f'{video_format}+bestaudio',
        'outtmpl': f'tmp{settings.FILE_DELIMITER}{filename}',
        'progress_hooks': [yt_dl_hook],
        # 'merge_output_format': 'mp4',
    }
    os.chdir(settings.DOWNLOAD_PATH)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except youtube_dl.utils.DownloadError as exc:
            dbase.sset(y_id, video_format, 'error', f'{exc.__class__.__name__}: {exc}')
            raise
    dbase.sset(y_id, video_format, 'status', 100)
