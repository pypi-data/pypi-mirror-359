from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

class Notification(BaseModel):
    id: UUID
    userId: Optional[UUID] = None
    type: Optional[str] = None
    body: Optional[str] = None
    contentId: Optional[UUID] = None
    publishedAt: Optional[datetime] = None
    expiresAt: Optional[datetime] = None
    read: Optional[bool] = None
