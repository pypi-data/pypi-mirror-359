from pydantic import BaseModel
from uuid import UUID
from extopy.com.extopy.models.users.User import User
from typing import Optional
from datetime import datetime
from typing import Any

class Post(BaseModel):
    id: UUID
    userId: UUID
    user: Optional[User] = None
    repliedToId: Optional[UUID] = None
    repostOfId: Optional[UUID] = None
    body: Optional[str] = None
    publishedAt: datetime
    editedAt: Optional[datetime] = None
    expiresAt: Optional[datetime] = None
    visibility: Optional[str] = None
    likesCount: Optional[int] = None
    repliesCount: Optional[int] = None
    repostsCount: Optional[int] = None
    likesIn: Optional[bool] = None
    parentId: Any
