from pydantic import BaseModel
from uuid import UUID

class AuthToken(BaseModel):
    accessToken: str
    refreshToken: str
    idToken: UUID
