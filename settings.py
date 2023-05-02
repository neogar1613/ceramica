import dotenv
import os
from logging import Formatter


ENVFILE_PATH = ".env"
DOCS_URL = '/docs'
REDOC_URL = '/redoc'
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8000
LOGDIR = 'logs'
LOGGER_DEFAULT_LEVEL = 'DEBUG'
LOGGER_DEFAULT_FORMAT = Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s')

if not os.path.exists(ENVFILE_PATH):
    print("[X] env variables is not loaded!")
    raise RuntimeError('Отсутствует .env файл!')

dotenv.load_dotenv(ENVFILE_PATH)

DEBUG = os.environ.get('DEBUG', True)
DATABASE_URL = os.environ.get('DATABASE_URL', "postgresql+asyncpg://postgres:postgres@0.0.0.0:5433/postgres")
TEST_DATABASE_URL = os.environ.get('TEST_DATABASE_URL', "postgresql+asyncpg://postgres_test:postgres_test@0.0.0.0:5434/postgres_test")

ACCESS_TOKEN_EXPIRE_MINUTES = 10
JWT_SECRET_KEY = "mkdlnfjkger7647y534j0tJJFHJE90e9e"
JWT_ALGORITHM = "sha256"

