from datetime import datetime, timedelta, timezone
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

from ..config import ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from ..db import create_user, get_user
from ..status import InvalidCredentials
from ..utils import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_db(request)
    user = await get_user(db, form_data.username)

    if not user or not bcrypt.checkpw(
        form_data.password.encode(), user.hashed_password.encode()
    ):
        raise InvalidCredentials("Wrong Login Credentials")

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode(
        {"sub": user.username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register")
async def register(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_db(request)
    username = form_data.username

    user = await get_user(db, username)
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = bcrypt.hashpw(form_data.password.encode(), bcrypt.gensalt()).decode()
    did_create = await create_user(db, username, hashed_pw, role="user")
    if not did_create:
        raise HTTPException(status_code=400, detail="Error creating user")

    return {"status": "User created"}
