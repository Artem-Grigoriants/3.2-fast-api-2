from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# --- Схемы для Пользователей (User) ---
#Базовый класс
class UserBase(BaseModel):
    username: str
    role: str = "user"  # По дефолту обычный юзер, можно менять на 'admin'

# Используется для ручки (endpoint) входа в систему. Проверяет, что пришли именно логин и пароль.
class UserLogin(BaseModel):  # Эта схема не определена, используется в main.py
    username: str
    password: str

#Используется при регистрации. Наследует username от UserBase и добавляет обязательное поле password.
class UserCreate(UserBase):
    password: str

#Используется для ответа сервера.
class UserResponse(UserBase):
    id: int
    role: Optional[str] = None
    # Пароль здесь не указываем, чтобы не светить его в API

#Используется для PATCH запросов (частичное обновление)
class UserUpdate(BaseModel):
    usermame: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


    class Config:
        from_attributes = True

# --- Схемы для Аутентификации (Auth) ---

#Это "форма", которую заполняет юзер, чтобы получить токен.
class Login(BaseModel):
    username: str
    password: str

#Это схема ответа при успешном входе.
class Token(BaseModel):
    access_token: str
    token_type: str

# --- Схемы для Объявлений (Advertisement) ---

#Общие поля: заголовок, описание, цена.
class AdvertisementBase(BaseModel):
    title: str
    description: str
    price: float

#Схема для создания объявления
class AdvertisementCreate(AdvertisementBase):
    # Здесь нет поля author, так как автор проставляется автоматически из токена
    pass

#Для редактирования объявления.
class AdvertisementUpdate(BaseModel):
    # Добавил схему для обновления (PATCH/PUT), где все поля опциональны
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

#То, что видит пользователь, просматривая объявления
class AdvertisementResponse(AdvertisementBase):
    id: int
    created_at: datetime
    author: str  # Здесь мы будем возвращать имя автора (username) из @property в models.py

    class Config:
        from_attributes = True