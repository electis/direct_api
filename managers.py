"""Надстройки, расширяющие функционал моделей"""
import os
from typing import Optional, Tuple

import httpx
import serializers
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
        self.video = models.DB().jget(self.y_id, 'info', {})

    async def check_file(self) -> Optional[str]:
        """Проверяет существование файла для скачивания, возвращает имя файла"""
        filename_ext = None
        filename = models.YouTube.filename.format(y_id=self.y_id, format=self.format)
        for ext in ['mkv', 'mp4']:
            if os.path.isfile(os.path.join(settings.DOWNLOAD_PATH, f'{filename}.{ext}')):
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
            if models.DB().sget(self.y_id, self.format, 'error'):
                raise YouTubeDownloadError('Ошибка при скачивании видео')
            url = None
            status = models.DB().sget(self.y_id, self.format, 'status')
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
                (format_.get('asr') and format_['fps']) or ((format_.get('height') or 0) > 720)  # with audio
            ) and (  # high quality
                format_.get('container') != 'webm_dash'
            )  # no webm

        formats = {f['format_id']: [f['format_note']] for f in self.video['formats'] if criteria(f)}
        return formats


class Inform:

    def __init__(self, data: dict, additional: dict = None):
        self.data = data
        self.additional = additional or dict()
        self.tg_id = self.data.get('tg_id', settings.INFORM_TG_ID)

    @staticmethod
    async def send_tg(text, tg_id=None):
        tg_id = tg_id or settings.INFORM_TG_ID
        url = f"https://api.telegram.org/bot{settings.INFORM_TG_TOKEN}/sendMessage" \
              f"?chat_id={tg_id}&parse_mode=Markdown&text={text}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.text

    async def inform(self):
        if settings.INFORM_TG_TOKEN and self.tg_id:
            text = "** direct\n"
            for key, value in self.additional.items():
                text += f"{key}: {value}\n"
            text += "** data\n"
            for key, value in self.data.items():
                text += f"{key}: {value}\n"
            await self.send_tg(text, self.tg_id)
