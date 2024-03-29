import os
import datetime
from dotenv import load_dotenv

load_dotenv()  # Load the environment variables from the ..env file

GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
GOOGLE_SECRET_KEY = os.environ['GOOGLE_SECRET_KEY']
DB_NAME = 'tanakhs'
CHAPTERS_COLLECTION_NAME = 'chapters'
USERS_COLLECTION = 'users'


class Config(object):
    CACHE_TYPE = os.environ['CACHE_TYPE']
    CACHE_REDIS_HOST = os.environ['CACHE_REDIS_HOST']
    CACHE_REDIS_PORT = os.environ['CACHE_REDIS_PORT']
    CACHE_REDIS_DB = os.environ['CACHE_REDIS_DB']
    CACHE_REDIS_URL = os.environ['CACHE_REDIS_URL']
    CACHE_DEFAULT_TIMEOUT = os.environ['CACHE_DEFAULT_TIMEOUT']
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    JWT_ALGORITHM = os.environ['JWT_ALGORITHM']
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)
