from pydantic import BaseModel
from extopy.com.extopy.models.application.Client import Client
from extopy.com.extopy.models.users.User import User

class ClientForUser(BaseModel):
    client: Client
    user: User
