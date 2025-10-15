from app.database.utils import get_user
from .security import get_username_from_request
from slowapi import Limiter


def get_rate_limit_by_role(key: str) -> str:
    if user := get_user(key):
        rbl = {'admin': '6/minute', 'user': '4/minute'}
        return rbl.get(user.role)
    return '2/minute'


limiter = Limiter(key_func=get_username_from_request)
