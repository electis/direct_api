"""
social services, class name = service name, methods: post, ...
"""
import json
from hashlib import md5
from abc import ABC, abstractmethod
from typing import Union

import requests
import vk_api

import settings
from exceptions import AuthError, UrlError, PostError
from helpers import logger
from serializers import Message, VKData, OKData


def url_exists(path: str) -> bool:
    """Проверяет url на доступность"""
    response = requests.head(path, timeout=1)
    return response.status_code == 200


class Service(ABC):
    """Шаблонный метод для сервисов соцсетей"""

    async def post_message(self, message: Message, data: Union[VKData, OKData]) -> str:
        """Шаблон постинга в соцсеть"""
        msg = await self.make_message(message=message)
        auth = await self.get_auth(data=data, msg=msg)
        result = await self.post(msg=msg, auth=auth)
        return result

    @abstractmethod
    async def make_message(self, message: Message) -> dict:
        """Подготавливаем сообщение"""

    @abstractmethod
    async def get_auth(self, data: Union[VKData, OKData], msg: dict) -> dict:
        """Добавляем данные авторизации"""

    @abstractmethod
    async def post(self, msg: dict, auth: dict) -> str:
        """post message to social service"""

    @abstractmethod
    def auth(self, login, password) -> str:
        """
        provide auth in social service
        :param login:
        :param password:
        :return: access token
        """


class Logger(Service):
    """Декоратор для логирования"""

    _obj: Service

    def __init__(self, obj):
        self._obj = obj

    @logger
    async def make_message(self, message: Message) -> dict:
        return await self._obj.make_message(message)

    @logger
    async def get_auth(self, data: Union[VKData, OKData], msg: dict) -> dict:
        return await self._obj.get_auth(data, msg)

    @logger(debug=settings.DEBUG)
    async def post(self, msg: dict, auth: dict) -> str:
        return await self._obj.post(msg, auth)

    @logger
    def auth(self, login, password) -> str:
        return self._obj.auth(login, password)


class VK(Service):
    """Вконтакте"""

    async def make_message(self, message: Message) -> dict:
        pict = message.pict
        if pict and not url_exists(pict):
            raise UrlError("pict not found")
        return dict(message=message.text, attachments=pict)

    async def get_auth(self, data: VKData, msg: dict) -> dict:  # type: ignore
        session = vk_api.VkApi(token=data.token).get_api()
        return dict(session=session, owner_id=data.owner_id)

    async def post(self, msg: dict, auth: dict) -> str:
        result = auth['session'].wall.post(owner_id=auth['owner_id'], **msg)
        if isinstance(result, dict) and 'post_id' in result:
            return result['post_id']
        raise PostError(str(result))

    @staticmethod
    def two_factor():
        """Набросок для двухфакторки"""
        code = input('Code? ')
        remember_device = True
        return code, remember_device

    def auth(self, login, password):
        # https://github.com/python273/vk_api/blob/master/examples/auth_by_code.py
        # https://ru.stackoverflow.com/questions/528715
        vk_session = vk_api.VkApi(login, password, auth_handler=VK.two_factor)
        try:
            vk_session.auth()
        except vk_api.AuthError as exc:
            raise AuthError from exc
        token = vk_session.token
        # result = vk.wall.get(owner_id=owner_id)
        # print(vk_session.token)
        return token


class OK(Service):
    """Одноклассники"""

    api_url = 'https://api.ok.ru/fb.do'

    async def make_message(self, message: Message):
        media = []
        if message.text:
            media.append(dict(type='text', text=message.text))
        if message.pict:
            media.append(self.load_image(message.pict))
        return dict(
            attachment=json.dumps({"media": media}),
            method="mediatopic.post",
            type="GROUP_THEME",
        )

    async def get_auth(self, data: OKData, msg: dict) -> dict:  # type: ignore
        params = dict(application_key=data.application_key, gid=data.gid, access_token=data.access_token, **msg)
        sig = self.get_sig(
            params,
            application_secret_key=data.application_secret_key,
            access_token=data.access_token,
        )
        params['sig'] = sig
        del params['method']
        return params

    async def post(self, msg: dict, auth: dict) -> str:
        result = self.call("mediatopic.post", **auth)
        return result

    def auth(self, login, password) -> str:
        ...

    def load_image(self, image_url):
        """Подгрузка картинки в ОК"""
        url = self.call("photosV2.getUploadUrl", count=1)
        response = requests.post(url, data=dict(image=image_url))
        if response.status_code == 200:
            key, token = response.json()['photos'].items()[0]
            self.call("photosV2.commit", photo_id=key, token=token)
        else:
            token = None
        return token

    def call(self, method: str, **params):
        """Вызов метода в ОК"""
        params['method'] = method
        response = requests.post(self.api_url, data=params)
        if response.status_code == 200:
            return response.text
        raise PostError(response.status_code)

    @staticmethod
    def get_sig(params: dict, session_secret_key=None, session=True, application_secret_key=None, access_token=None):
        """Подпись поста для ОК"""
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
