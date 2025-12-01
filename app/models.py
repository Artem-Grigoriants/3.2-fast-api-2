import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
#from app.database import get_db

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)  # Здесь будет храниться хэш пароля
    role = Column(String, default="user")      # Роль по умолчанию — "user"

    # Связь с объявлениями: один пользователь — много объявлений
    advertisements = relationship("Advertisement", back_populates="user")


class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Ссылка на id пользователя (ForeignKey)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Связь для удобного доступа к объекту пользователя (ad.user)
    user = relationship("User", back_populates="advertisements")
    @property
    def author(self):
        # Возвращаем username связанного пользователя
        return self.user.username