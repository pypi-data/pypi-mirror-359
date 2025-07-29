from pydantic import BaseModel

class SearchOptions(BaseModel):
    search: str
