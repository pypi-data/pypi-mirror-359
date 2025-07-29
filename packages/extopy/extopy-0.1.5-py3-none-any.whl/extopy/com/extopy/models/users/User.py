from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime
from typing import Any

class User(BaseModel):
    id: UUID
    displayName: str
    username: str
    email: Optional[str] = None
    password: Optional[str] = None
    biography: Optional[str] = None
    avatar: Optional[str] = None
    birthdate: Optional[datetime] = None
    joinDate: Optional[datetime] = None
    lastActive: Optional[datetime] = None
    personal: Optional[bool] = None
    verified: Optional[bool] = None
    banned: Optional[bool] = None
    postsCount: Optional[int] = None
    followersCount: Optional[int] = None
    followingCount: Optional[int] = None
    followersIn: Optional[bool] = None
    followingIn: Optional[bool] = None
    parentId: Any
