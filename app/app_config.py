import os
from typing import List
from urllib.parse import quote_plus

from decouple import Csv, config

# Core Settings
ALLOWED_HOSTS: List[str] = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())
API_VERSION = "1.0.0"
DEBUG = config("DEBUG", default=False, cast=bool)

# Database Settings
POSTGRES_HOST = config("POSTGRES_HOST", default="localhost")
POSTGRES_PORT = config("POSTGRES_PORT", default=5432, cast=int)
POSTGRES_USER = config("POSTGRES_USER", default="postgres")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", default="postgres")
POSTGRES_NAME = config("POSTGRES_NAME", default="code_editor")
POSTGRES_POOL_SIZE = config("POSTGRES_POOL_SIZE", default=5, cast=int)
POSTGRES_MAX_OVERFLOW = config('POSTGRES_MAX_OVERFLOW', default=10, cast=int)

# Redis Settings
REDIS_HOST = config("REDIS_HOST", default="localhost")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
REDIS_DB = config("REDIS_DB", default=0, cast=int)
REDIS_PASSWORD = config("REDIS_PASSWORD", default=None)

# JWT Settings
JWT_SECRET_KEY = config("JWT_SECRET_KEY", default="your-secret-key")
JWT_ALGORITHM = config("JWT_ALGORITHM", default="HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = config("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)

# OpenAI Settings
OPENAI_API_KEY = config("OPENAI_API_KEY")
OPENAI_API_MODEL = config("OPENAI_API_MODEL", default="gpt-3.5-turbo")
