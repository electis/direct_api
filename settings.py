import os

from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')
SECRET_TOKEN = os.getenv('SECRET_TOKEN', 'not_secure')
if ENVIRONMENT == 'production':
    assert SECRET_TOKEN != 'not_secure', 'Token not secure'

REDIS = os.getenv('REDIS', 'redis://localhost:6379/1')
REDIS_DB = int(os.getenv('REDIS_DB', '1'))

DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH', '/storage/youtube')
DOWNLOAD_URL = os.getenv('DOWNLOAD_URL', 'http://192.168.0.5/download/')
