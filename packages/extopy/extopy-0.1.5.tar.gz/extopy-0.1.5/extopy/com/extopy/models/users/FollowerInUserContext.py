from pydantic import BaseModel
from uuid import UUID

class FollowerInUserContext(BaseModel):
    userId: UUID
    isTargetPublic: bool
