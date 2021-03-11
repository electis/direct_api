import os

TG_API_URL = 'https://api.telegram.org'

SECRET_TOKEN = os.getenv('SECRET_TOKEN', 'not_secure')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')

REDIS = 'redis://localhost:6379/1'
DOWNLOAD_PATH = '/storage/youtube'
