import os

import redis
import youtube_dl

import tasks


class YouTube(object):

    def __init__(self, y_id):
        self.y_id = y_id
        self.url = f'http://www.youtube.com/watch?v={y_id}'

    def check_status(self, format):
        filename = f"{self.y_id}_{format}"
        try:
            size = os.path.getsize(f'{filename}.mp4')
        except FileNotFoundError:
            return "0"
        video = self.extract_info()
        video_size = 0
        for f in video['formats']:
            if f['format_id'] == format:
                video_size = f['filesize']
        if not video_size:
            return None
        return size / video_size * 100

    def download(self, format):
        filename = f"{self.y_id}_{format}"
        redis_name = f'youtube_download_{filename}'
        data = dict()

        r = redis.Redis()
        status = r.get(redis_name)

        if status is None:
            tasks.youtube_download(self.y_id, format)
        else:
            if status == b'100':
                download_url = f'http://youtube.electis.ru/download/{filename}.mp4'
                data['url'] = download_url
            # else:
            #     status = self.check_status(format)

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

    def info(self):
        video = self.extract_info()

        criteria = lambda f: bool(f.get('asr') and f['fps'])  # with audio

        formats = {f['format_id']: [f['format_note'], f['vcodec']]
                   for f in video['formats']
                   if criteria(f)}
        data = dict(
            id=video['id'],
            title=video['title'],
            description=video['description'],
            duration=video['duration'],
            thumbnail=video['thumbnail'],
            formats=formats
        )
        return data

    def clear(self):
        filename = f"{self.y_id}_{format}"
        os.remove(filename)
        redis_name = f'youtube_download_{filename}'
        r = redis.Redis()
        r.delete(redis_name)
