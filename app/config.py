import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env (если он есть)
load_dotenv()

# Читаем переменные (второй аргумент - значение по умолчанию, если переменной нет)
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "aeg19802402")
DB_NAME = os.getenv("POSTGRES_DB", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

# Формируем строку подключения (DSN)
# Используем драйвер asyncpg для асинхронной работы
PG_DSN = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

