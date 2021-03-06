from environs import Env

env = Env()
env.read_env('../env')


SECRET_KEY = env('SECRET_KEY')
SQLALCHEMY_DATABASE_URI = env('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
JSON_SORT_KEYS = False

MAIL_SERVER = 'smtp-relay.sendinblue.com'
MAIL_PORT = 587
MAIL_USERNAME = env('SMTP_USERNAME')
MAIL_PASSWORD = env('SMTP_PASS')
MAIL_USE_TLS = True
MAIL_USE_SSL = False


REDIS_HOST = 'localhost'
CACHE_TYPE = 'redis'
CACHE_REDIS_PORT = 6379
CACHE_REDIS_URL = env("CACHE_REDIS_URL")

# In minutes
LOGIN_URL_LIFETIME = env.int('LOGIN_URL_LIFETIME')
ACCESS_TOKEN_LIFETIME = env.int('ACCESS_TOKEN_LIFETIME')
REFRESH_TOKEN_LIFETIME = env.int('REFRESH_TOKEN_LIFETIME')


CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")
