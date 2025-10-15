"""Модели Pydantic для API."""
from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List
from datetime import datetime


class ChartBase(BaseModel):
    title: str
    description: Optional[str] = None
    chart_type: str


class ChartCreate(ChartBase):
    organization_id: int


class ChartOut(ChartBase):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    organization_id: int

    class Config:
        from_attributes = True


class OrganizationBase(BaseModel):
    name: str
    iiko_api_key: Optional[str] = None


class OrganizationOut(OrganizationBase):
    id: int
    users: List[int] = []

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def validate_password(cls, v):
        """Валидация пароля."""
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        return v


class UserResponce(UserBase):
    id: int
    is_admin: bool
    organizations: List[int] = []

    class Config:
        from_attributes = True


class UserInDB(UserResponce):
    hashed_password: str = Field(exclude=True)


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
