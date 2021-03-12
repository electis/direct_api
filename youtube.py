import os

import youtube_dl

import settings
from tasks import youtube_download, redis_con


class YouTube(object):

    def __init__(self, y_id):
        self.y_id = y_id
        self.url = f'http://www.youtube.com/watch?v={y_id}'

    def download(self, format, background_tasks):
        filename = f"{self.y_id}_{format}"
        redis_name = f'youtube_download_{filename}'
        data = dict()

        filename_ext = None
        for ext in ['mkv', 'mp4']:
            if os.path.isfile(os.path.join(settings.DOWNLOAD_PATH, f'{filename}.{ext}')):
                filename_ext = f'{filename}.{ext}'
                break

        if filename_ext:
            status = 100
            download_url = f'{settings.DOWNLOAD_URL}{filename_ext}'
            data['url'] = download_url
        else:
            status = redis_con.get(redis_name)
            if status is None:
                background_tasks.add_task(youtube_download, self.y_id, format)
                # youtube_download(self.y_id, format)

        data['status'] = status
        return data

    def extract_info(self):
        # TODO cache something
        with youtube_dl.YoutubeDL() as ydl:
            try:
                video = ydl.extract_info(self.url, download=False)
            except youtube_dl.utils.DownloadError as exc:
                raise
        if 'entries' in video:
            video = video['entries'][0]  # Can be a playlist or a list of videos
        return video

    def info(self, format=None):
        video = self.extract_info()

        criteria = lambda f: (((f.get('asr') and f['fps'])
                               or ((f.get('height') or 0) > 720))
                              and (f.get('container') != 'webm_dash'))
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
        if format:
            filename = f"{self.y_id}_{format}"
            filename_ext = None
            for ext in ['mkv', 'mp4']:
                if os.path.isfile(os.path.join(settings.DOWNLOAD_PATH, f'{filename}.{ext}')):
                    filename_ext = f'{filename}.{ext}'
                    break
            if filename_ext:
                status = 100
                download_url = f'{settings.DOWNLOAD_URL}{filename_ext}'
                data['url'] = download_url
            else:
                redis_name = f'youtube_download_{filename}'
                status = redis_con.get(redis_name)
            data['status'] = status
        return data

    def clear(self):
        filename = f"{self.y_id}_{format}"
        os.remove(filename)
        redis_name = f'youtube_download_{filename}'
        redis_con.delete(redis_name)
