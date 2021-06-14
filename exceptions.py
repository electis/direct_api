"""Исключения для ручного вызова"""


class YouTubeDownloadError(Exception):
    """Ошибка скачивания видео"""


class AuthError(Exception):
    """Ошибка аутентификации на стороннем сервисе"""


class UrlError(Exception):
    """Ошибка проверки ссылки"""
