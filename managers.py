import os
from typing import Optional, Tuple

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

    async def check_file(self) -> Optional[str]:
        filename_ext = None
        filename = models.YouTube.filename.format(y_id=self.y_id, format=self.format)
        for ext in ['mkv', 'mp4']:
            if os.path.isfile(os.path.join(settings.DOWNLOAD_PATH, f'{filename}.{ext}')):
                filename_ext = f'{filename}.{ext}'
                break
        return filename_ext

    async def check_status(self)-> Tuple[Optional[str], str]:
        filename = await self.check_file()
        if filename:
            url = f'{settings.DOWNLOAD_URL}{filename}'
            status = '100'
        else:
            if models.cache.sget(self.y_id, self.format, 'error'):
                raise Exception('DownloadError')
            url = None
            status = models.cache.sget(self.y_id, self.format, 'status')
        return status, url

    async def get_info(self) -> dict:
        if not self.video:
            self.video = await models.YouTube().extract_info(self.y_id)
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
