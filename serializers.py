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


class Youtube(BaseModel):
    y_id: str
    format: Optional[str] = None
    download: Optional[bool] = False


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
    status: str = None
    url: str = None
    y_id: str
    title: str = None
    description: str = None
    duration: str = None
    thumbnail: str = None
    filtered_formats: dict = None


class YouTubeResult(BaseModel):
    error: Optional[str]
    data: Optional[YoutubeData]


class YoutubeInfo(BaseModel):
    y_id: str
    format: Optional[str] = None


class YoutubeDownload(BaseModel):
    y_id: str
    format: str
