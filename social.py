"""
social services, class name = service name, methods: post, ...
"""
import json
from hashlib import md5
from abc import ABC, abstractmethod
from typing import Union

import requests
import vk_api

from exceptions import AuthError, UrlError, PostError
from serializers import Message, VKData, OKData


def url_exists(path) -> Union[bool, str]:
    r = requests.head(path)
    return r.status_code == requests.codes.ok


class Abstract(ABC):
    """Шаблонный метод для сервисов соцсетей"""

    def post_message(self, message: Message, data: Union[VKData, OKData]) -> Union[int, str, None]:
        """Шаблон постинга в соцсеть"""
        msg = self.make_message(message=message)
        auth = self.get_auth(data=data, msg=msg)
        result = self.post(msg=msg, auth=auth)
        return result

    @abstractmethod
    def make_message(self, message: Message):
        """Подготавливаем сообщение"""

    @abstractmethod
    def get_auth(self, data:  Union[VKData, OKData], msg: dict):
        """Добавляем данные авторизации"""

    @abstractmethod
    def post(self, msg: dict, auth: dict) -> str:
        """post message to social service"""

    @abstractmethod
    def auth(self, login, password) -> str:
        """
        provide auth in social service
        :param login:
        :param password:
        :return: access token
        """


class VK(Abstract):

    def make_message(self, message: Message):
        pict = message.pict
        if pict and not url_exists(pict):
            raise UrlError("pict not found")
        return dict(message=message.text, attachments=pict)

    def get_auth(self, data: VKData, **kwargs):
        session = vk_api.VkApi(token=data.token).get_api()
        return dict(session=session, owner_id=data.owner_id)

    def post(self, msg: dict, auth: dict):
        result = auth['session'].wall.post(owner_id=auth['owner_id'], **msg)
        if isinstance(result, dict) and 'post_id' in result:
            return result['post_id']
        raise PostError(str(result))

    @staticmethod
    def two_factor():
        code = input('Code? ')
        remember_device = True
        return code, remember_device

    def auth(self, login, password):
        # https://github.com/python273/vk_api/blob/master/examples/auth_by_code.py
        # https://ru.stackoverflow.com/questions/528715
        vk_session = vk_api.VkApi(login, password, auth_handler=VK.two_factor)
        try:
            vk_session.auth()
        except vk_api.AuthError:
            raise AuthError
        token = vk_session.token
        # result = vk.wall.get(owner_id=owner_id)
        # print(vk_session.token)
        return token


class OK(Abstract):
    api_url = 'https://api.ok.ru/fb.do'

    def make_message(self, message: Message):
        media = []
        if message.text:
            media.append(dict(type='text', text=message.text))
        if message.pict:
            media.append(self.load_image(message.pict))
        return dict(attachment=json.dumps({"media": media}), method="mediatopic.post", type="GROUP_THEME",)

    def get_auth(self, data: OKData, msg: dict):
        params = dict(
            application_key=data.application_key,
            gid=data.gid,
            access_token=data.access_token,
            **msg
        )
        sig = self.get_sig(
            params,
            application_secret_key=data.application_secret_key,
            access_token=data.access_token,
        )
        params['sig'] = sig
        del params['method']
        return params

    def post(self, auth: dict, **kwargs):
        self.call("mediatopic.post", **auth)

    def auth(self, login, password) -> str:
        ...

    def load_image(self, image_url):
        url = self.call("photosV2.getUploadUrl", count=1)
        response = requests.post(url, data=dict(image=image_url))
        if response.status_code == 200:
            key, token = response.json()['photos'].items()[0]
            self.call("photosV2.commit", photo_id=key, token=token)
        else:
            token = None
        return token

    def call(self, method: str, **params):
        params['method'] = method
        response = requests.post(self.api_url, data=params)
        if response.status_code == 200:
            return response.text
        raise PostError(response.text)

    @staticmethod
    def get_sig(
        params: dict,
        session_secret_key=None,
        session=True,
        application_secret_key=None,
        access_token=None,
    ):
        if not session_secret_key:
            if not session:
                session_secret_key = application_secret_key
            else:
                session_secret_key = md5(f"{access_token}{application_secret_key}".encode('utf-8')).hexdigest().lower()
        exclude_keys = {'session_key', 'access_token'}
        params_str = ''.join([f'{key}={params[key]}' for key in sorted(params.keys()) if key not in exclude_keys])
        params_str += session_secret_key
        sig = md5(params_str.encode('utf-8')).hexdigest().lower()
        return sig
