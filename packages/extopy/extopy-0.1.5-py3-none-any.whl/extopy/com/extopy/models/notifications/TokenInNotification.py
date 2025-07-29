from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from extopy.com.extopy.models.users.User import User
from typing import Optional

class TokenInNotification(BaseModel):
    token: str
    service: str
    clientId: UUID
    userId: UUID
    expiresAt: datetime
    user: Optional[User] = None
