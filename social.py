'''
social services, class name = service name, methods: post, ...
'''
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Union, Literal, Optional

import requests
import vk_api
from ok_api import OkApi, Upload

SERVICES = Literal['VK', 'OK']


def url_exists(path) -> Union[bool, str]:
    r = requests.head(path)
    return r.status_code == requests.codes.ok


class Message(BaseModel):
    text: Optional[str]
    pict: Optional[str]


class UserData(BaseModel):
    token: str
    owner_id: str
    gid: Optional[str]
    uid: Optional[str]


class ServiceData(BaseModel):
    access_token: Optional[str]
    application_key: Optional[str]
    application_secret_key: Optional[str]


class ServiceFactory(ABC):
    @abstractmethod
    def post(self, message: Message, user_data: UserData, service_data: ServiceData) -> Union[int, str, None]:
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
    def post(self, message: Message, user_data: UserData, service_data: ServiceData = None) -> Union[int, str, None]:
        vk_session = vk_api.VkApi(token=user_data.token)
        owner_id = user_data.owner_id
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
    def post(self, message: Message, user_data: UserData, service_data: ServiceData) -> Union[int, str, None]:
        # https://apiok.ru/dev/methods/rest/mediatopic/mediatopic.post
        ok = OkApi(access_token=service_data.access_token,  # or service access?
                   application_key=service_data.application_key,
                   application_secret_key=service_data.application_secret_key)
        response = ok.friends.get(sort_type='PRESENT')
        print(response.json())
        media = []
        if message.text:
            media.append({
                "type": "text",
                "text": message.text
            })
        if message.pict:
            # TODO нужен путь к картинке, а в ВК - урл
            pict_path = message.pict
            upload = Upload(ok)
            upload_response = upload.photo(photos=[pict_path])
            # TODO надо?
            for photo_id in upload_response['photos']:
                token = upload_response['photos'][photo_id]['token']
                response = ok.photosV2.commit(photo_id=photo_id, token=token)
            media.append({
                "type": "photo",
                "list": [
                    {"id": list(upload_response['photos'].keys())[0]},
                    {"photoId": response.json()['photos'][0]['assigned_photo_id']},
                ]
            })
        params = {
            # 'text_link_preview': True,  # Обрабатывать ссылку в тексте
            'attachment': {
                'media': media
            }
        }
        # если пост в группу
        if user_data.gid:
            params.update({
                'gid': user_data.gid,
                'type': 'GROUP_THEME',
            })
        else:
            params.update({
                'uid': user_data.uid,
            })
        result = ok.mediatopic.post(**params)
        if result.status_code != 200:
            raise Exception(f'OK status_code: {result.status_code}')
        result_json = result.json()
        # TODO {'error_code': 104, 'error_msg': 'PARAM_SIGNATURE : Invalid signature f71f55844d96fa53b74b560fb6a955c2, calculated by string application_key=CCNDIMJGDIHBABABAattachment=mediagid=58695245955153method=mediatopic.posttext_link_preview=Truetype=GROUP_THEME********SECRET KEY*******', 'error_data': None}
        print(result_json)
        if 'error_code' in result_json:
            raise Exception(f'OK error: {result_json}')
        return

    def auth(self, login, password) -> str:
        pass
