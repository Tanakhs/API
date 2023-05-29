import json
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .objectid import PydanticObjectId


class Comment(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    name: str
    email: str
    picture: str
    content: str
    date_added: Optional[datetime] = datetime.now()
    date_updated: Optional[datetime] = datetime.now()

    def to_json(self):
        return json.loads(self.json())

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if "_id" in data and data["_id"] is None:
            data.pop("_id")
        return data
