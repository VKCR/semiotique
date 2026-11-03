from datetime import datetime

from pydantic import BaseModel


class Note(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    categories: list[str]
    links: list[str]
    content: str
    embedding: list[float]
