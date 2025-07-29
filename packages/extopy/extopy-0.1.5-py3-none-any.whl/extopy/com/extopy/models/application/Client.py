from pydantic import BaseModel
from uuid import UUID
from typing import Any

class Client(BaseModel):
    id: UUID
    ownerId: UUID
    name: str
    description: str
    secret: str
    redirectUri: str
    parentId: Any
