from pydantic import BaseModel
from datetime import datetime

class CreateUserPayload(BaseModel):
    username: str
    displayName: str
    email: str
    password: str
    birthdate: datetime
