from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .connection import get_db
from app.models.models import User
from app.models.schemas import UserResponce
from app.middleware.logging import logger

router = APIRouter()


@router.get("/users", response_model=List[UserResponce])
async def get_users(db: AsyncSession = Depends(get_db)) -> List[User]:
    try:
        result = await db.execute(select(User))
        users = result.scalars().all()
        return users
    except Exception as e:
        logger.error(f"Ошибка при получении пользователей: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/user/{username}", response_model=UserResponce)
async def get_user(username: str, db: AsyncSession = Depends(get_db)) -> User:
    try:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя {username}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
