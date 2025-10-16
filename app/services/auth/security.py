import jwt
from app.config.settings import config
from app.database.connection import get_db
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
# from pwdlib.hashers.bcrypt import BcryptHasher
from app.models.schemas import UserInDB
from app.models.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.middleware.logging import logger


oauth2pb = OAuth2PasswordBearer(tokenUrl="login", auto_error=True)
auth_headers = {"WWW-Authenticate": "Bearer"}
# ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
ctx = PasswordHash.recommended()


async def get_user_by_username(
    username: str,
    db: AsyncSession
) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def auth_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> User:
    user = await get_user_by_username(form_data.username, db)
    if not user:
        logger.warning(f"User not found: {form_data.username}")
        raise HTTPException(status_code=404, detail="User not found", headers=auth_headers)
    if not ctx.verify(form_data.password, user.hashed_password):
        logger.warning(f"Invalid password for {form_data.username}")
        raise HTTPException(status_code=401, detail="Authorization failed", headers=auth_headers)
    return user


def create_jwt(data: dict) -> str:
    d = data.copy() | {'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=config.jwt.access_token_ttl)}
    return jwt.encode(d, config.jwt.secret_key.get_secret_value(), algorithm=config.jwt.algorithm)


def decode_jwt(token: str | None) -> dict:
    try:
        return jwt.decode(token, config.jwt.secret_key.get_secret_value(), algorithms=[config.jwt.algorithm])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(status_code=401, detail="Invalid or expired token", headers=auth_headers)


def get_access_token(token: str | None = Depends(oauth2pb)) -> str | None:
    return token


def create_hashed_password(password: str) -> str:
    return ctx.hash(password)


async def get_user_from_jwt(token: str | None = Depends(get_access_token)) -> UserInDB:
    payload = decode_jwt(token)
    user = await get_user_by_username(payload['sub'])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_username_from_request(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    token = auth_header.split()[-1] if auth_header else None
    try:
        payload = decode_jwt(token)
        return payload.get("sub", "_guest")
    except HTTPException:
        return "_guest"
