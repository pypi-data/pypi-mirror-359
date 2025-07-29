from pydantic import BaseModel

class Email(BaseModel):
    title: str
    body: str
