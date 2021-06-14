"""Сериализация и проверка используемых в проекте объектов"""
from typing import Optional, Union, Literal

from pydantic import BaseModel

SERVICES = Literal['VK', 'OK']


class Message(BaseModel):
    """Сообщение для отправки в соцсеть"""

    text: Optional[str]
    pict: Optional[str]


class OKData(BaseModel):
    """Данные для работы с ОК"""

    access_token: str
    gid: str
    application_id: str
    application_key: str
    application_secret_key: str


class VKData(BaseModel):
    """Данные для работы с ВК"""

    token: str
    owner_id: str


class Social(BaseModel):
    """входящий запрос на отправку в соцсеть"""

    service: SERVICES
    data: Union[OKData, VKData]
    message: Message


class Result(BaseModel):
    """основной ответ сервиса"""

    result: Optional[str]
    error: Optional[str]


class YoutubeData(BaseModel):
    """данные о видео с YouTube"""

    status: Optional[str]
    url: Optional[str]
    y_id: str
    title: Optional[str]
    description: Optional[str]
    duration: Optional[str]
    thumbnail: Optional[str]
    filtered_formats: Optional[dict]


class YouTubeInfoResult(BaseModel):
    """ответ сервиса по данным о видео"""

    error: Optional[str]
    data: Optional[YoutubeData]


class YoutubeDownloadData(BaseModel):
    """информация по скачиваемому видео"""

    status: Optional[str]
    url: Optional[str]
    y_id: str


class YoutubeDownloadResult(BaseModel):
    """ответ сервиса по запросу на скачивание видео"""

    error: Optional[str]
    data: Optional[YoutubeDownloadData]


class YoutubeDownload(BaseModel):
    """входящий запрос на скачивание видео"""

    y_id: str
    format: str
