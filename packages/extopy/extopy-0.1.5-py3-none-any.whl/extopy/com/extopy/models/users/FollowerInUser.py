from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from extopy.com.extopy.models.users.User import User

class FollowerInUser(BaseModel):
    userId: UUID
    targetId: UUID
    accepted: Optional[bool] = None
    user: Optional[User] = None
    target: Optional[User] = None
