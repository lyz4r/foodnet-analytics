from app.database.utils import get_user
from fastapi import Depends, APIRouter, HTTPException, Request
from .utils import get_rate_limit_by_role, limiter
from .rbac import PermissionChecker
from app.models.schemas import UserBase, UserCreate, UserInDB, Token
from app.models.models import User
from .security import auth_user, create_jwt, get_user_from_jwt, create_hashed_password, get_access_token, get_user_by_username
from app.database.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.middleware.logging import logger

router = APIRouter()


@router.post('/login', response_model=Token)
async def login(current_user: UserBase = Depends(auth_user)):
    """Маршрут для аутентификации, возвращает токен"""
    return Token(access_token=create_jwt({'sub': current_user.username}))


@router.post('/signup', response_model=Token)
async def signup(new_user: UserCreate, db: AsyncSession = Depends(get_db)) -> Token:
    """Маршрут для регистрации, возвращает токен"""
    db_user = await get_user_by_username(new_user.username, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    hashed_password = create_hashed_password(new_user.password)
    try:
        user_in_db = User(username=new_user.username, email=new_user.email, hashed_password=hashed_password)
        db.add(user_in_db)
        db.commit()
    except Exception as e:
        logger.error(f"Ошибка создания пользователя {new_user.username}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Ошибка создания пользователя {new_user.username}")
    return get_access_token(Token(access_token=create_jwt({'sub': new_user.username})))


@router.get('/protected_resource/{username}')
@PermissionChecker("admin", "user")
@limiter.limit(get_rate_limit_by_role)
async def protected_resource(request: Request, username: str, user: UserBase = Depends(get_user_from_jwt)):
    """Маршрут для пользователей / администраторов с параметром пути. Админ может просматривать информацию о любом
    пользователе, а пользователь - только о себе."""
    if user.role == 'admin':
        return get_user(username)
    elif user.username == username:
        return user
    raise HTTPException(status_code=403, detail="Доступ запрещён")


@router.get("/admin")
@PermissionChecker("admin")
@limiter.limit(get_rate_limit_by_role)
async def admin_endpoint(request: Request, cur_user: UserBase = Depends(get_user_from_jwt)):
    """Маршрут для администраторов"""
    return {"message": f"Hello, {cur_user.username}! Welcome to the admin page."}


@router.get("/user")
@PermissionChecker("user")
@limiter.limit(get_rate_limit_by_role)
async def user_endpoint(request: Request, user: UserBase = Depends(get_user_from_jwt)):
    """Маршрут для пользователей"""
    if user:
        return {"message": f"Hello, {user.username}! Welcome to the user page."}
    raise HTTPException(status_code=401, detail='Not authorized')


@router.get("/guest")
@limiter.limit(get_rate_limit_by_role)
async def guest_endpoint(request: Request):
    """Маршрут для гостей"""
    return {"message": "Hello, guest! Welcome to the guest page."}
