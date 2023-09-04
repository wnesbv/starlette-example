
from datetime import datetime

from pydantic import BaseModel


class FormCreate(BaseModel):
    title: str
    description: str | None = None
    created_at: datetime
    owner: int


class FormUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    modified_at: datetime


class DBItem(BaseModel):
    id: int
    title: str
    description: str | None = None
    file: str | None = None
    created_at: datetime
    modified_at: datetime | None = None
    owner: int

    class Config:
        from_attributes = True


class ListItem(BaseModel):
    each_item: list[DBItem]
