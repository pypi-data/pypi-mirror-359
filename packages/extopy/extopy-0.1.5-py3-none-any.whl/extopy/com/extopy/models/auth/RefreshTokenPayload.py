from pydantic import BaseModel

class RefreshTokenPayload(BaseModel):
    refreshToken: str
