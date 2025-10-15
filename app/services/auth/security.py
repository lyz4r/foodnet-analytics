import jwt
from app.config.settings import config
from app.database.utils import get_user
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from app.models.schemas import UserInDB


oauth2pb = OAuth2PasswordBearer(tokenUrl="login", auto_error=True)
auth_headers = {"WWW-Authenticate": "Bearer"}
ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def auth_user(current_user: OAuth2PasswordRequestForm = Depends()) -> UserInDB:
    user = await get_user(current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found", headers=auth_headers)
    if not ctx.verify(current_user.password, user.hashed_password):
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


async def get_user_from_jwt(token: str | None = Depends(get_access_token)) -> UserInDB:
    payload = decode_jwt(token)
    user = await get_user(payload['sub'])
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
