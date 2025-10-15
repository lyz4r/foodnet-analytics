from app.database.utils import get_user
from fastapi import Depends, APIRouter, HTTPException, Request
from .utils import get_rate_limit_by_role, limiter
from .rbac import PermissionChecker
from app.models.schemas import UserBase, Token
from .security import auth_user, create_jwt, get_user_from_jwt

router = APIRouter()


@router.post('/login', response_model=Token)
async def login(current_user: UserBase = Depends(auth_user)):
    """Маршрут для аутентификации, возвращает токен"""
    return Token(access_token=create_jwt({'sub': current_user.username}))


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
