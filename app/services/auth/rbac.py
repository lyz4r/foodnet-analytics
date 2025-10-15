from fastapi import HTTPException, status
from functools import wraps


class PermissionChecker:
    def __init__(self, *allowed_roles: str):
        self.allowed_roles = allowed_roles

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("user")
            if not user or user.role not in self.allowed_roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")
            return await func(*args, **kwargs)
        return wrapper
