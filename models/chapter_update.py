from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

from .objectid import PydanticObjectId


class HollyBook(Enum):
    THE_OLD_TESTAMENT = 1
    THE_NEW_TESTAMENT = 2
    QURAN = 3


class ChapterUpdate(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    author: str
    holy_book: HollyBook = HollyBook.THE_OLD_TESTAMENT
    book: str
    chapter_number: int
    chapter_letters: str
    verses: List[str]
    analysis: str
    rating: dict
    tags: List[str]
    date_added: Optional[datetime] = datetime.now()
    date_updated: Optional[datetime] = datetime.now()

    def to_json(self):
        return self.json()

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        data["holy_book"] = data["holy_book"].value
        if "_id" in data and data["_id"] is None:
            data.pop("_id")
        return data
