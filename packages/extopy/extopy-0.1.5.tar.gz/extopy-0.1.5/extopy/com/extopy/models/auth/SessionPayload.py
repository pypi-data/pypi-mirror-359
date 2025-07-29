from pydantic import BaseModel
from uuid import UUID

class SessionPayload(BaseModel):
    userId: UUID
