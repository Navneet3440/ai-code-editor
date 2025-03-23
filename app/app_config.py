import os
from decouple import Csv, config
from urllib.parse import quote_plus

# Core Settings
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())
API_VERSION = "1.0.0"
DEBUG = True
# DB config
POSTGRES_HOST = os.getenv('POSTGRES_HOST').strip()
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT').strip())
POSTGRES_USER = os.getenv('POSTGRES_USER').strip()
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD').strip()
POSTGRES_NAME = os.getenv('POSTGRES_NAME').strip()
POSTGRES_POOL_SIZE = config('POSTGRES_POOL_SIZE', default=5, cast=int)
POSTGRES_MAX_OVERFLOW = config('POSTGRES_MAX_OVERFLOW', default=10, cast=int)

# Redis Config
REDIS_HOST = os.getenv('REDIS_HOST').strip()
REDIS_PORT = int(os.getenv('REDIS_PORT').strip())
REDIS_DB = int(os.getenv('REDIS_DB').strip())
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD').strip()

# JWT Config
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY').strip()
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM').strip()
JWT_EXPIRE_MINUTES = int(os.getenv('JWT_EXPIRE_MINUTES').strip())

# OPENAI Config
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY').strip()
OPENAI_API_MODEL = os.getenv('OPENAI_API_MODEL').strip()