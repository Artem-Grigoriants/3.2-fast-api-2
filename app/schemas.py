from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# --- Схемы для Пользователей (User) ---

class UserBase(BaseModel):
    username: str
    role: str = "user"  # По дефолту обычный юзер, можно менять на 'admin'

# отсутствующая схема login
class UserLogin(BaseModel):  # Эта схема не определена, используется в main.py
    username: str
    password: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    # Пароль здесь не указываем, чтобы не светить его в API

    class Config:
        from_attributes = True

# --- Схемы для Аутентификации (Auth) ---

class Login(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Схемы для Объявлений (Advertisement) ---

class AdvertisementBase(BaseModel):
    title: str
    description: str
    price: int

class AdvertisementCreate(AdvertisementBase):
    # Здесь нет поля author, так как автор проставляется автоматически из токена
    pass

class AdvertisementUpdate(BaseModel):
    # Добавил схему для обновления (PATCH/PUT), где все поля опциональны
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class AdvertisementResponse(AdvertisementBase):
    id: int
    created_at: datetime
    author: str  # Здесь мы будем возвращать имя автора (username) из @property в models.py

    class Config:
        from_attributes = True