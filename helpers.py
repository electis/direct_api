"""Вспомогательные функции"""
import functools

import settings
from models import DB


def output(message: str, dest='console'):
    """Выводит сообщение в переданный dest"""
    methods = dict(
        console=print,
    )
    methods[dest](message)


def logger(func=None, *, debug=False, dest='console'):
    """Декоратор для логирования"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            output(func.__qualname__, dest)
            if debug:
                output(str(kwargs), dest)
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                output(str(exc), dest)
                raise
            if debug:
                output(result, dest)
            return result

        return wrapper

    if func:
        return decorator(func)
    return decorator


def calc_status(status, min_perc, max_perc):
    """Преобразует процент скачивания в пределы mix и max"""
    return int(min_perc + (max_perc - min_perc) * status / 100)


def set_status(y_id, video_format, downloading_format, status):
    """сохраняет текущий прогресс скачивания в преобразованном виде"""
    dbase = DB()
    d_format = dbase.sget(y_id, video_format, 'd_format')
    if d_format is None:
        dbase.sset(y_id, video_format, 'd_format', downloading_format)
        d_part = 0
        dbase.sset(y_id, video_format, 'd_part', d_part)
    elif d_format != downloading_format:
        dbase.sset(y_id, video_format, 'd_format', downloading_format)
        d_part = 1
        dbase.sset(y_id, video_format, 'd_part', d_part)
    else:
        d_part = int(dbase.sget(y_id, video_format, 'd_part'))
    part_perc = ((1, 70), (71, 95))
    full_status = calc_status(status, *part_perc[d_part])
    dbase.sset(y_id, video_format, 'status', full_status)


def yt_dl_hook(info):
    """хук прогресса скачивания"""
    _, y_id, video_format, downloading_format = info['filename'].split(settings.FILE_DELIMITER)
    if info['status'] == 'downloading':
        status = int(float(info.get('_percent_str', '0').strip('%')))
        set_status(y_id, video_format, downloading_format, status)
