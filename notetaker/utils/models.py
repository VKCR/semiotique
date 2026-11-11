from datetime import datetime

from pydantic import BaseModel


class Note(BaseModel):
    id: str
    created_at: datetime
    categories: list[str]
    linked_ids: list[str]
    content: str
    embedding: list[float]
