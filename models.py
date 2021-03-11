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
    data: Optional[dict]
