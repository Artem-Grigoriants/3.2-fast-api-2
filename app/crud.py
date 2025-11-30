from sqlalchemy.orm import Session
from . import models, schemas


# --- ADVERTISEMENTS ---

def create_advertisement(db: Session, ad: schemas.AdvertisementCreate, user_id: int):
    # Распаковываем данные объявления и добавляем ID пользователя-автора
    db_ad = models.Advertisement(**ad.model_dump(), user_id=user_id)
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad


def get_advertisement(db: Session, ad_id: int):
    return db.query(models.Advertisement).filter(models.Advertisement.id == ad_id).first()


def update_advertisement(db: Session, ad_id: int, ad_data: schemas.AdvertisementCreate):
    # exclude_unset=True важно, чтобы не перезатереть поля значениями None, если они не были переданы
    db.query(models.Advertisement).filter(models.Advertisement.id == ad_id).update(
        ad_data.model_dump(exclude_unset=True))
    db.commit()
    return get_advertisement(db, ad_id)


def delete_advertisement(db: Session, ad_id: int):
    db.query(models.Advertisement).filter(models.Advertisement.id == ad_id).delete()
    db.commit()


def search_advertisements(db: Session, title: str = None, author: str = None):
    query = db.query(models.Advertisement)
    if title:
        query = query.filter(models.Advertisement.title.ilike(f"%{title}%"))
    if author:
        # ВНИМАНИЕ: Если author теперь это связь через user_id, то поиск по имени автора
        # должен выглядеть как join с таблицей User.
        # Если в модели Advertisement поле author осталось как строка, этот код сработает.
        # Если author теперь relationship, нужно делать так:
        # query = query.join(models.User).filter(models.User.username.ilike(f"%{author}%"))
        query = query.filter(models.Advertisement.author.ilike(f"%{author}%"))
    return query.all()


# --- USERS ---

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    # Превращаем Pydantic модель в словарь
    user_data = user.model_dump()

    # Удаляем сырой пароль, если он есть в схеме, чтобы не сохранить его в БД случайно
    if "password" in user_data:
        del user_data["password"]

    # Создаем модель пользователя, передавая хэш пароля явно
    db_user = models.User(**user_data, password=hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_data: schemas.UserCreate):
    # Обратите внимание: здесь используется UserCreate, но для обновления часто создают отдельную схему UserUpdate
    db.query(models.User).filter(models.User.id == user_id).update(user_data.model_dump(exclude_unset=True))
    db.commit()
    return get_user(db, user_id)


def delete_user(db: Session, user_id: int):
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()