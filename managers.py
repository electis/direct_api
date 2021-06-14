"""Надстройки, расширяющие функционал моделей"""
import os
from typing import Optional, Tuple

from exceptions import YouTubeDownloadError
import settings
import models


class YouTube:
    """Дополнительные методы для работы с YouTube"""

    y_id: Optional[str]
    format: Optional[str]
    video: dict

    def __init__(self, y_id, video_format=None):
        self.y_id = y_id
        self.format = video_format
        self.video = models.cache.jget(self.y_id, 'info', {})

    async def check_file(self) -> Optional[str]:
        """Проверяет существование файла для скачивания, возвращает имя файла"""
        filename_ext = None
        filename = models.YouTube.filename.format(y_id=self.y_id, format=self.format)
        for ext in ['mkv', 'mp4']:
            if os.path.isfile(
                os.path.join(settings.DOWNLOAD_PATH, f'{filename}.{ext}')
            ):
                filename_ext = f'{filename}.{ext}'
                break
        return filename_ext

    async def check_status(self) -> Tuple[Optional[str], Optional[str]]:
        """Возвращает статус скачивания файла и имя файла, если уже скачан"""
        url: Optional[str]
        filename = await self.check_file()
        if filename:
            url = f'{settings.DOWNLOAD_URL}{filename}'
            status = '100'
        else:
            if models.cache.sget(self.y_id, self.format, 'error'):
                raise YouTubeDownloadError('Ошибка при скачивании видео')
            url = None
            status = models.cache.sget(self.y_id, self.format, 'status')
        return status, url

    async def get_info(self) -> dict:
        """Получает информацию о видео"""
        if not self.video:
            self.video = await models.YouTube().extract_info(self.y_id)
        return self.video

    def filter_formats(self) -> dict:
        """Отфильтровывает доступные форматы видео по определённому правилу"""
        if not self.video:
            return {}

        def criteria(format_):
            return (
                (format_.get('asr') and format_['fps'])  # with audio
                or ((format_.get('height') or 0) > 720)
            ) and (  # high quality
                format_.get('container') != 'webm_dash'
            )  # no webm

        formats = {
            f['format_id']: [f['format_note']]
            for f in self.video['formats']
            if criteria(f)
        }
        return formats
