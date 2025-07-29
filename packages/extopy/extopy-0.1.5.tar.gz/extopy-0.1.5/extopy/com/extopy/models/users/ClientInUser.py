from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ClientInUser(BaseModel):
    code: str
    userId: UUID
    clientId: UUID
    expiration: datetime
