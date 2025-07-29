from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class AuthRequest(BaseModel):
    clientId: UUID
    clientSecret: str
    code: str
    codeVerifier: Optional[str] = None
