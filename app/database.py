from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Строка подключения
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db/postgres"

# 2. Создание движка (engine)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Базовый класс для моделей
Base = declarative_base()

# 5. Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()