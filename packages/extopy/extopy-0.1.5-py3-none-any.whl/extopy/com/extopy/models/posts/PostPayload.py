from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class PostPayload(BaseModel):
    body: str
    repliedToId: Optional[UUID] = None
    repostOfId: Optional[UUID] = None
