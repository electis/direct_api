import os

import youtube_dl

import settings
from models import cache, YouTube


def calc_status(status, min_perc, max_perc):
    return int(min_perc + (max_perc - min_perc) * status / 100)


def set_status(y_id, video_format, downloading_format, status):
    d_format = cache.sget(y_id, video_format, 'd_format')
    if d_format is None:
        cache.sset(y_id, video_format, 'd_format', downloading_format)
        d_part = 0
        cache.sset(y_id, video_format, 'd_part', d_part)
    elif d_format != downloading_format:
        cache.sset(y_id, video_format, 'd_format', downloading_format)
        d_part = 1
        cache.sset(y_id, video_format, 'd_part', d_part)
    else:
        d_part = int(cache.sget(y_id, video_format, 'd_part'))
    part_perc = (
        (1, 70), (71, 95)
    )
    full_status = calc_status(status, *part_perc[d_part])
    cache.sset(y_id, video_format, 'status', full_status)


def my_hook(d):
    _, y_id, video_format, downloading_format = d['filename'].split(settings.FILE_DELIMITER)
    if d['status'] == 'downloading':
        status = int(float(d.get('_percent_str', '0').strip('%')))
        set_status(y_id, video_format, downloading_format, status)


def youtube_download(y_id, video_format):
    status = cache.sget(y_id, video_format, 'status')
    if status:
        print('Already running?')
        return

    cache.sset(y_id, video_format, 'status', 0)
    filename = YouTube.filename.format(y_id=y_id, format=video_format)
    url = YouTube.url_format.format(y_id)
    ydl_opts = {
        'postprocessors': [{
            'key': 'ExecAfterDownload',
            # TODO can be mkv
            'exec_cmd': 'mv {} ' + f'{filename}.mp4'
        }],
        'format': f'{video_format}+bestaudio',
        'outtmpl': f'tmp{settings.FILE_DELIMITER}{filename}',
        'progress_hooks': [my_hook],
        # 'merge_output_format': 'mp4',
    }
    os.chdir(settings.DOWNLOAD_PATH)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except youtube_dl.utils.DownloadError as exc:
            cache.sset(y_id, video_format, 'error', f'{exc.__class__.__name__}: {exc}')
            raise
    cache.sset(y_id, video_format, 'status', 100)
