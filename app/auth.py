import jwt
from app.models import User, get_db
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# === КОНФИГУРАЦИЯ ===
SECRET_KEY = "SECRET FOR MY CODE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 48  # Срок жизни токена

# Настройка для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Схема авторизации (указывает, откуда брать токен и куда слать за логином)
# tokenUrl="login" означает, что если токена нет, Swagger UI предложит сходить на /login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# === 1. ХЭШИРОВАНИЕ И ПРОВЕРКА ПАРОЛЕЙ ===

def hash_password(password: str) -> str:
    """Хэширует пароль перед сохранением в БД."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, совпадает ли введенный пароль с хэшем в БД."""
    return pwd_context.verify(plain_password, hashed_password)


# === 2. РАБОТА С JWT ТОКЕНАМИ ===

def create_access_token(data: dict) -> str:
    """Создает JWT токен с данными пользователя и сроком жизни."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    # Добавляем время истечения (exp) в полезную нагрузку токена
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# === 3. ЗАВИСИМОСТЬ (DEPENDENCY) ДЛЯ ЗАЩИТЫ РОУТОВ ===

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Эта функция будет использоваться в роутах как Depends(get_current_user).
    Она:
    1. Достает токен из заголовка Authorization.
    2. Проверяет его валидность и срок жизни.
    3. Достает user_id (или username) из токена.
    4. Ищет пользователя в БД.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Декодируем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Достаем имя пользователя (обычно оно кладется в поле 'sub')
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

    except jwt.PyJWTError:
        # Ошибка возникает, если токен просрочен или подделан
        raise credentials_exception

    # Ищем пользователя в базе данных
    # ВАЖНО: Убедись, что у твоей модели User есть поле username
    user = db.query(User).filter(User.username == username).first()

    if user is None:
        raise credentials_exception

    return user