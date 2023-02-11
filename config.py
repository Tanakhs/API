import os
from dotenv import load_dotenv

load_dotenv()  # Load the environment variables from the .env file


class Config(object):
    CACHE_TYPE = os.environ['CACHE_TYPE']
    CACHE_REDIS_HOST = os.environ['CACHE_REDIS_HOST']
    CACHE_REDIS_PORT = os.environ['CACHE_REDIS_PORT']
    CACHE_REDIS_DB = os.environ['CACHE_REDIS_DB']
    CACHE_REDIS_URL = os.environ['CACHE_REDIS_URL']
    CACHE_DEFAULT_TIMEOUT = os.environ['CACHE_DEFAULT_TIMEOUT']

    def __init__(self):
        print(f"CACHE_TYPE: {self.CACHE_TYPE}")
        print(f"CACHE_REDIS_HOST: {self.CACHE_REDIS_HOST}")
        print(f"CACHE_REDIS_PORT: {self.CACHE_REDIS_PORT}")
        print(f"CACHE_REDIS_DB: {self.CACHE_REDIS_DB}")
        print(f"CACHE_REDIS_URL: {self.CACHE_REDIS_URL}")
        print(f"CACHE_DEFAULT_TIMEOUT: {self.CACHE_DEFAULT_TIMEOUT}")
