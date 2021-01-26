'''
social services, class name = service name, methods: post, ...
'''
import json
from hashlib import md5
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Union, Literal, Optional

import requests
import vk_api

SERVICES = Literal['VK', 'OK']


def url_exists(path) -> Union[bool, str]:
    r = requests.head(path)
    return r.status_code == requests.codes.ok


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


class ServiceFactory(ABC):
    @abstractmethod
    def post(self, message: Message, data: Union[VKData, OKData]) -> Union[int, str, None]:
        '''
        post message to social service
        :return: post_id or None
        '''
        pass

    @abstractmethod
    def auth(self, login, password) -> str:
        '''
        provide auth in social service
        :param login:
        :param password:
        :return: access token
        '''
        pass


class VK(ServiceFactory):
    # TODO подгружать фото на вк, а не атачем. Сделать видео.
    def post(self, message: Message, data: VKData) -> Union[int, str, None]:
        vk_session = vk_api.VkApi(token=data.token)
        owner_id = data.owner_id
        pict = message.pict
        if pict and not url_exists(pict):
            raise Exception("pict not found")
        vk = vk_session.get_api()
        try:
            result = vk.wall.post(message=message.text, attachments=pict, owner_id=owner_id)
        except Exception as exc:
            raise
        if isinstance(result, dict) and 'post_id' in result:
            return result['post_id']

    @staticmethod
    def two_factor():
        code = input('Code? ')
        remember_device = True
        return code, remember_device

    def auth(self, login, password):
        # https://github.com/python273/vk_api/blob/master/examples/auth_by_code.py
        # https://ru.stackoverflow.com/questions/528715/%D0%9F%D0%BE%D1%81%D1%82%D0%B8%D0%BD%D0%B3-%D0%B2-vk-%D1%87%D0%B5%D1%80%D0%B5%D0%B7-vk-api-python
        vk_session = vk_api.VkApi(login, password, auth_handler=VK.two_factor)
        try:
            vk_session.auth()
        except vk_api.AuthError as exc:
            raise
        token = vk_session.token
        # result = vk.wall.get(owner_id=owner_id)
        # print(vk_session.token)
        return token


class OK(ServiceFactory):
    def post(self, message: Message, data: OKData) -> Union[int, str, None]:
        # url = 'https://api.ok.ru/api'
        url = 'https://api.ok.ru/fb.do'
        application_secret_key = data.application_secret_key
        access_token = data.access_token
        media = [{"type": "text", "text": "wqe"}]
        params = {
            "application_key": data.application_key,
            "attachment": {"media": media},
            "gid": data.gid,
            "method": "mediatopic.post",
            "type": "GROUP_THEME",
            "access_token": access_token
        }
        sig = self.get_sig(params, application_secret_key=application_secret_key, access_token=access_token)
        params['sig'] = sig
        test = requests.post(url, data=params)
        return f'{test.status_code} {test.text}'

    def auth(self, login, password) -> str:
        pass

    @staticmethod
    def get_sig(params: dict, session_secret_key=None, session=True, application_secret_key=None, access_token=None):
        if not session_secret_key:
            if not session:
                session_secret_key = application_secret_key
            else:
                session_secret_key = md5(f"{access_token}{application_secret_key}".encode('utf-8')).hexdigest().lower()
        exclude_keys = {'session_key', 'access_token'}
        params_str = ''.join([f'{key}={params[key] if isinstance(params[key], str) else json.dumps(params[key])}'
                              for key in sorted(params.keys()) if not key in exclude_keys])
        params_str += session_secret_key
        sig = md5(params_str.encode('utf-8')).hexdigest().lower()
        # TODO не правильный sig
        return sig
