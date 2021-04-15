import os

import youtube_dl

import settings
from tasks import youtube_download
from utils import cache


class YouTube(object):

    def __init__(self, y_id):
        self.y_id = y_id
        self.url = f'http://www.youtube.com/watch?v={y_id}'

    def download(self, v_format, background_tasks):
        filename = f"{self.y_id}.{v_format}"
        data = dict()

        filename_ext = None
        for ext in ['mkv', 'mp4']:
            if os.path.isfile(os.path.join(settings.DOWNLOAD_PATH, f'{filename}.{ext}')):
                filename_ext = f'{filename}.{ext}'
                break
        if filename_ext:
            status = '100'
            download_url = f'{settings.DOWNLOAD_URL}{filename_ext}'
            data['url'] = download_url
        else:
            status = cache.sget(self.y_id, v_format, 'status')
            if status is None:
                background_tasks.add_task(youtube_download, self.y_id, v_format)
                # youtube_download(self.y_id, format)
        data['status'] = status
        return data

    def extract_info(self):
        video = cache.jget(self.y_id, 'info')
        if video:
            return video
        with youtube_dl.YoutubeDL() as ydl:
            try:
                video = ydl.extract_info(self.url, download=False)
            except youtube_dl.utils.DownloadError:
                raise
        if 'entries' in video:
            video = video['entries'][0]  # Can be a playlist or a list of videos
        cache.jset(self.y_id, 'info', video)
        return video

    def info(self, v_format=None):
        video = self.extract_info()

        criteria = lambda f: (((f.get('asr') and f['fps'])  # with audio
                               or ((f.get('height') or 0) > 720))  # high quality
                              and (f.get('container') != 'webm_dash'))  # no webm
        formats = {f['format_id']: [f['format_note']]
                   for f in video['formats']
                   if criteria(f)}

        data = dict(
            id=video['id'],
            title=video['title'],
            description=video['description'],
            duration=video['duration'],
            thumbnail=video['thumbnail'],
            formats=formats,
        )
        if v_format:
            filename = f"{self.y_id}_{v_format}"
            filename_ext = None
            for ext in ['mkv', 'mp4']:
                if os.path.isfile(os.path.join(settings.DOWNLOAD_PATH, f'{filename}.{ext}')):
                    filename_ext = f'{filename}.{ext}'
                    break
            if filename_ext:
                status = '100'
                download_url = f'{settings.DOWNLOAD_URL}{filename_ext}'
                data['url'] = download_url
            else:
                status = cache.sget(self.y_id, v_format, 'status')
            data['status'] = status
        return data

    def clear(self):
        ...
        filename = f"{self.y_id}.*"
        os.removexattr(settings.DOWNLOAD_PATH, filename)
        cache.del_one(self.y_id)
