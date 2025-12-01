from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, crud, database, auth
from .database import engine
from .models import User, Advertisement

# Создаем таблицы (лучше использовать Alembic для миграций, но пока оставим так)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Зависимость для получения сессии БД
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- РОУТЫ АВТОРИЗАЦИИ И ПОЛЬЗОВАТЕЛЕЙ ---

@app.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    1. Найти пользователя по username.
    2. Проверить пароль.
    3. Вернуть токен.
    """
    # Ищем пользователя (функцию get_user_by_username нужно добавить в crud.py)
    user = crud.get_user_by_username(db, username=user_data.username)

    if not user:
        # В целях безопасности лучше возвращать общее сообщение
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    # Проверяем пароль (функция из auth.py)
    if not auth.verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    # Создаем токен (функция из auth.py)
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/user", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    1. Проверить, нет ли уже такого юзера.
    2. ПРОВЕРИТЬ, ЧТО НЕ ПЫТАЮТСЯ СОЗДАТЬ АДМИНА.
    3. Захэшировать пароль.
    4. Сохранить.
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    if user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Creating admin users is not allowed via public registration"
        )
    # Хэшируем пароль перед отправкой в CRUD
    hashed_password = auth.hash_password(user.password)

    # Создаем юзера (функцию create_user нужно обновить в crud.py, чтобы она принимала хэш)
    return crud.create_user(db=db, user=user, hashed_password=hashed_password)


@app.get("/user/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Найти и вернуть пользователя по ID."""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.patch("/user/{user_id}", response_model=schemas.UserResponse)
def update_user(
        user_id: int,
        user_update: schemas.UserUpdate, #Определили схему
        db: Session = Depends(get_db),
        current_user: User = Depends(auth.get_current_user)
):
    """Обновление пользователя. Только сам юзер или админ."""

    # Проверка прав
    if current_user.id != user_id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Вызываем CRUD
    return crud.update_user(db, user_id, user_update)  # Исправлено в crud



@app.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth.get_current_user)
):
    """Удаление пользователя. Только сам юзер или админ."""

    # Проверка прав
    if current_user.id != user_id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_user(db, user_id)
    return None


@app.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: User = Depends(auth.get_current_user)):
    """Получить текущего залогиненного пользователя."""
    return current_user


# --- РОУТЫ ОБЪЯВЛЕНИЙ (ADVERTISEMENT) ---

@app.post("/advertisement/", response_model=schemas.AdvertisementResponse, status_code=status.HTTP_201_CREATED)
def create_ad(
        ad: schemas.AdvertisementCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth.get_current_user)
):
    """Создание объявления. Привязываем user_id текущего пользователя."""
    # Передаем ID пользователя в CRUD функцию
    return crud.create_advertisement(db, ad, user_id=current_user.id)


@app.get("/advertisement/{ad_id}", response_model=schemas.AdvertisementResponse)
def read_ad(ad_id: int, db: Session = Depends(get_db)):
    ad = crud.get_advertisement(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad


@app.patch("/advertisement/{ad_id}", response_model=schemas.AdvertisementResponse)
def update_ad(
        ad_id: int,
        ad_update: schemas.AdvertisementCreate,  # Или отдельная схема Update
        db: Session = Depends(get_db),
        current_user: User = Depends(auth.get_current_user)
):
    """Обновление объявления. Владелец или админ."""
    # 1. Находим объявление
    db_ad = crud.get_advertisement(db, ad_id)
    if not db_ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    # 2. Проверяем права
    if db_ad.user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 3. Обновляем
    return crud.update_advertisement(db, ad_id, ad_update)


@app.delete("/advertisement/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ad(
        ad_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth.get_current_user)
):
    """Удаление объявления. Владелец или админ."""
    # 1. Находим объявление
    db_ad = crud.get_advertisement(db, ad_id)
    if not db_ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    # 2. Проверяем права
    if db_ad.user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 3. Удаляем
    crud.delete_advertisement(db, ad_id)
    return None


@app.get("/advertisement/", response_model=List[schemas.AdvertisementResponse])
def search_ads(
        title: str = Query(None),
        author: str = Query(None), #Исправлено с int = user_id
        db: Session = Depends(get_db)
):
    return crud.search_advertisements(db, title, author)