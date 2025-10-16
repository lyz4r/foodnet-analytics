"""Модели Pydantic для API."""
from pydantic import BaseModel, EmailStr, field_validator, Field, ConfigDict
from typing import Optional, List, Dict, Any


class ChartData(BaseModel):
    data: List[Dict[str, Any]]
    chart_type: str
    x_field: str
    y_field: str
    color_field: Optional[str] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("chart_type")
    @classmethod
    def validate_chart_type(cls, v: str) -> str:
        allowed_types = {"line", "bar", "scatter", "pie"}
        if v not in allowed_types:
            raise ValueError(f"Тип графика должен быть одним из {allowed_types}, получено '{v}'")
        return v

    @field_validator("data")
    @classmethod
    def validate_data_not_empty(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not v:
            raise ValueError("Данные не могут быть пустыми")
        return v


class OrganizationBase(BaseModel):
    name: str
    iiko_api_key: Optional[str] = None


class OrganizationOut(OrganizationBase):
    id: int
    users: List[int] = []
    model_config = ConfigDict(arbitrary_types_allowed=True)


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
    is_admin: bool = False
    organizations: List[int] = []
    model_config = ConfigDict(arbitrary_types_allowed=True)


class UserInDB(UserBase):
    hashed_password: str = Field(exclude=True)


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
