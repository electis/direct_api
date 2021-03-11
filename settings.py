import os

TG_API_URL = 'https://api.telegram.org'

SECRET_TOKEN = os.getenv('SECRET_TOKEN', 'not_secure')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')

broker = 'redis://localhost:6379/7'
