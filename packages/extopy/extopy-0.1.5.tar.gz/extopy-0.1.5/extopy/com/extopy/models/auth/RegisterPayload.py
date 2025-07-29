from pydantic import BaseModel

class RegisterPayload(BaseModel):
    email: str
