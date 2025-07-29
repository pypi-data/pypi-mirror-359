from pydantic import BaseModel
from datetime import datetime

class RegisterCodePayload(BaseModel):
    password: str
    username: str
    displayName: str
    birthdate: datetime
