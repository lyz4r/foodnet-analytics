"""Модели SQLAlchemy для таблиц базы данных."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.database.connection import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=False)  # пароли храним только хешами!!!
    is_admin = Column(Boolean, default=False)

    charts = relationship("Chart", back_populates="user")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    iiko_api_key = Column(String, nullable=True)

    charts = relationship("Chart", back_populates="organization")


class Chart(Base):
    __tablename__ = "charts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    chart_type = Column(String, nullable=False)  # тип графика, например, "bar", "line", "pie" и т.д. мб пригодится, если что, вырежем
    created_at = Column(DateTime, nullable=False)  # временная метка создания графика
    updated_at = Column(DateTime, nullable=False)  # временная метка последнего обновления графика, изначально равна created_at
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # внешний ключ на таблицу users, показывает создателя графика
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)  # по аналогии

    user = relationship("User", back_populates="charts")
    organization = relationship("Organization", back_populates="charts")
