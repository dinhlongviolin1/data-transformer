from typing import Optional

from fastapi import Depends, Request, Security
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt

from .config import ALGORITHM, SECRET_KEY
from .db import get_user
from .models import User, UserRole
from .status import InsufficientPermission, InvalidCredentials
from .utils import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_current_user(
    request: Request, token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub", "")
        if username == "":
            raise InvalidCredentials()
        db = get_db(request)
        if user := await get_user(db, username):
            return user
        else:
            raise InvalidCredentials()
    except (ExpiredSignatureError, JWTError):
        raise InvalidCredentials()


async def admin_required(user=Depends(get_current_user)):
    if user.role != UserRole.admin:
        raise InsufficientPermission()
    return user


async def get_optional_user(
    request: Request, token: Optional[str] = Security(oauth2_scheme)
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise InvalidCredentials()
        db = get_db(request)
        return await get_user(db, username)
    except (ExpiredSignatureError, JWTError):
        raise InvalidCredentials()
