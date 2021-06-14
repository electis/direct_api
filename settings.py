"""основные настройки проекта, берутся из .env файла или из переменных окружения"""
import os

from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv('PORT', '8000'))

ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')
SECRET_TOKEN = os.getenv('SECRET_TOKEN', 'not_secure')
if ENVIRONMENT == 'production':
    assert SECRET_TOKEN != 'not_secure', 'Token not secure'

REDIS = os.getenv('REDIS', 'redis://localhost:6379/1')

DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH', '/storage/youtube')
DOWNLOAD_URL = os.getenv('DOWNLOAD_URL', 'http://192.168.0.5/download/')

FILE_DELIMITER = '.'
REDIS_DELIMITER = '|'
