import os

import settings
import models


class YouTube:
    y_id: str = None
    format: str = None
    video: dict = None

    def __init__(self, y_id, format=None):
        self.y_id = y_id
        self.format = format
        self.video = models.cache.jget(self.y_id, 'info', {})

    def check_status(self)-> (str, str):
        url = None
        filename_ext = None
        filename = f"{self.y_id}.{self.format}"
        for ext in ['mkv', 'mp4']:
            if os.path.isfile(os.path.join(settings.DOWNLOAD_PATH, f'{filename}.{ext}')):
                filename_ext = f'{filename}.{ext}'
                break

        if filename_ext:
            status = '100'
            url = f'{settings.DOWNLOAD_URL}{filename_ext}'
        else:
            status = models.cache.sget(self.y_id, self.format, 'status')
            if status == '100':
                status = None

        return status, url

    def get_info(self):
        youtube = models.YouTube(y_id=self.y_id).extract_info()
        self.video = youtube.video
        return self.video

    def filter_formats(self) -> dict:
        if not self.video:
            return {}
        criteria = lambda f: (((f.get('asr') and f['fps'])  # with audio
                               or ((f.get('height') or 0) > 720))  # high quality
                              and (f.get('container') != 'webm_dash'))  # no webm
        formats = {f['format_id']: [f['format_note']]
                   for f in self.video['formats']
                   if criteria(f)}
        return formats
