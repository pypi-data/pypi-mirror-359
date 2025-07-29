from pydantic import BaseModel
from typing import Optional

class UpdateUserPayload(BaseModel):
    username: Optional[str] = None
    displayName: Optional[str] = None
    password: Optional[str] = None
    biography: Optional[str] = None
    avatar: Optional[str] = None
    personal: Optional[bool] = None
