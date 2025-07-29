from pydantic import BaseModel
from uuid import UUID
from typing import Any

class Timeline(BaseModel):
    id: UUID
    parentId: Any
