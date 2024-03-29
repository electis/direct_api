"""Основные настройки проекта, берутся из .env файла или из переменных окружения"""
import os

from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig

load_dotenv(override=True)

PORT = int(os.getenv('PORT', '8000'))
HOST = os.getenv('HOST', '0.0.0.0')

SECRET_TOKEN = os.getenv('SECRET_TOKEN', 'very_secret_token')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')
DEBUG = True
if ENVIRONMENT == 'production':
    assert SECRET_TOKEN != 'very_secret_token', 'Token not secure'
    DEBUG = False

REDIS = os.getenv('REDIS', 'redis://localhost:6379/1')

DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH', '/storage/youtube')
DOWNLOAD_URL = os.getenv('DOWNLOAD_URL', 'http://192.168.0.5/download/')

INFORM_TG_TOKEN = os.getenv('INFORM_TG_TOKEN')
INFORM_TG_ID = os.getenv('INFORM_TG_ID')

MAIL_CONFIG = ConnectionConfig(
    MAIL_FROM=os.getenv('MAIL_FROM'),
    MAIL_USERNAME=os.getenv('MAIL_FROM'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_PORT=465,
    MAIL_SERVER="smtp.mail.ru",
    MAIL_FROM_NAME=os.getenv('MAIL_FROM_NAME'),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
)

FILE_DELIMITER = '.'
REDIS_DELIMITER = '|'
