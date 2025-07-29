from pydantic import BaseModel
from uuid import UUID

class UserContext(BaseModel):
    userId: UUID
