"""Модели SQLAlchemy для таблиц базы данных."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from app.database.connection import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)  # пароли храним только хешами!!!
    is_admin = Column(Boolean, default=False)

    charts = relationship("Chart", back_populates="user")
    uploads = relationship(
        "UserDataItem",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    iiko_api_key = Column(String, nullable=True)

    charts = relationship("Chart", back_populates="organization")

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"


class Chart(Base):
    __tablename__ = "charts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    chart_type = Column(String, nullable=False)  # тип графика, например, "bar", "line", "pie" и т.д.
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)

    user = relationship("User", back_populates="charts")
    organization = relationship("Organization", back_populates="charts")

    def __repr__(self):
        return f"<Chart(id={self.id}, title='{self.title}')>"


class DataItem(Base):  # возможно потом будет реализовано, метаданные о файлах, загруженных юзерами
    __tablename__ = "data_items"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    content_type = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    uploads = relationship(
        "UserDataItem",
        back_populates="data_item",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<DataItem(id={self.id}, filename='{self.filename}')>"


class UserDataItem(Base):
    __tablename__ = "user_data_items"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    data_id = Column(String, ForeignKey("data_items.id"), primary_key=True)
    uploaded_at = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship("User", back_populates="uploads")
    data_item = relationship("DataItem", back_populates="uploads")

    def __repr__(self):
        return f"<UserDataItem(user_id={self.user_id}, data_id={self.data_id}, uploaded_at={self.uploaded_at})>"
