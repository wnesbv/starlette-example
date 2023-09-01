from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DBItem(BaseModel):
    id: int
    title: str
    description: str
    file: str | None = None
    created_at: datetime
    modified_at: datetime | None = None
    item_owner: int

    class Config:
        from_attributes = True


class ListItem(BaseModel):
    each_item: list[DBItem]
