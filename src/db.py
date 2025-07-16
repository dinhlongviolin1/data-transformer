from typing import Optional

import bcrypt
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from .config import ADMIN_PASSWORD, ADMIN_USERNAME, DEFAULT_TRANSFORMS
from .logger import get_logger
from .models import User, UserRole


def get_user_db(db: AsyncIOMotorDatabase) -> AsyncIOMotorCollection:
    return db["users"]


async def get_admin_user(db: AsyncIOMotorDatabase) -> Optional[User]:
    return await get_user_db(db).find_one({"role": UserRole.admin})


async def create_admin_user_if_none(db: AsyncIOMotorDatabase):
    admin = await get_admin_user(db)
    if not admin:
        hashed_pw = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()

        await get_user_db(db).insert_one(
            {
                "username": ADMIN_USERNAME,
                "hashed_password": hashed_pw,
                "role": UserRole.admin,
                "allowed_transforms": None,
            }
        )
        get_logger().info(
            f"[INFO] Admin user created: {ADMIN_USERNAME} / {ADMIN_PASSWORD}"
        )


async def get_user(db: AsyncIOMotorDatabase, username: str) -> Optional[User]:
    user = await get_user_db(db).find_one({"username": username})
    return User(**user) if user else None


async def set_user_transforms(
    db: AsyncIOMotorDatabase, username: str, transforms: list[str]
):
    return await get_user_db(db).update_one(
        {"username": username}, {"$set": {"allowed_transforms": transforms}}
    )


async def get_user_allowed_transforms(
    db: AsyncIOMotorDatabase, username: Optional[str]
):
    if username is None:
        return DEFAULT_TRANSFORMS
    user = await get_user(db, username)
    if user is None:
        return DEFAULT_TRANSFORMS
    if user.role == UserRole.admin:
        return None
    return user.allowed_transforms or DEFAULT_TRANSFORMS


async def create_user(db, username: str, hashed_pw: str, role: str = "user") -> bool:
    if await get_user(db, username):
        return False
    try:
        user = User(
            username=username,
            hashed_password=hashed_pw,
            role=UserRole(role),
            allowed_transforms=DEFAULT_TRANSFORMS if role != UserRole.admin else None,
        )
        await get_user_db(db).insert_one(user.model_dump())
        return True
    except Exception:
        return False
