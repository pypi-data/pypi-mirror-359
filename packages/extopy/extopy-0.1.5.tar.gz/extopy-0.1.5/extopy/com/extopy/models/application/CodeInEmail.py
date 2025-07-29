from pydantic import BaseModel
from datetime import datetime

class CodeInEmail(BaseModel):
    email: str
    code: str
    expiresAt: datetime
