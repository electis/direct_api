from pydantic import BaseModel
from typing import Optional, Union, Literal

SERVICES = Literal['VK', 'OK']


class Message(BaseModel):
    text: Optional[str]
    pict: Optional[str]


class OKData(BaseModel):
    access_token: str
    gid: str
    application_id: str
    application_key: str
    application_secret_key: str


class VKData(BaseModel):
    token: str
    owner_id: str


class Social(BaseModel):
    service: SERVICES
    data: Union[OKData, VKData]
    message: Message


class Result(BaseModel):
    result: Optional[str]
    error: Optional[str]


class YoutubeData(BaseModel):
    status: Optional[str]
    url: Optional[str]
    y_id: str
    title: str = None
    description: str = None
    duration: str = None
    thumbnail: str = None
    filtered_formats: dict = None


class YouTubeInfoResult(BaseModel):
    error: Optional[str]
    data: Optional[YoutubeData]


class YoutubeDownloadData(BaseModel):
    status: Optional[str]
    url: Optional[str]
    y_id: str


class YoutubeDownloadResult(BaseModel):
    error: Optional[str]
    data: Optional[YoutubeDownloadData]


class YoutubeDownload(BaseModel):
    y_id: str
    format: str
