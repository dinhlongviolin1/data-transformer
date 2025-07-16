from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TransformRequest(BaseModel):
    data: List[Dict[str, Any]]
    pipeline: List[str]


class TransformConfig(BaseModel):
    enabled_transforms: List[str]


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class User(BaseModel):
    username: str
    hashed_password: str  # hashed
    role: UserRole = UserRole.user
    allowed_transforms: Optional[List[str]] = Field(default_factory=list)
