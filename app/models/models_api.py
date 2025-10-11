"""Модели Pydantic для API."""
from pydantic import BaseModel
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
        orm_mode = True


class OrganizationBase(BaseModel):
    name: str
    iiko_api_key: Optional[str] = None


class OrganizationOut(OrganizationBase):
    id: int
    users: List[int] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    is_admin: bool
    organizations: List[int] = []

    class Config:
        orm_mode = True
