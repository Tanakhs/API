from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from .objectid import PydanticObjectId


class Comment(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    user_name: str
    profile_picture_url: str
    content: str
    date_added: Optional[datetime] = datetime.now()
    date_updated: Optional[datetime] = datetime.now()

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        if "_id" in data and data["_id"] is None:
            data.pop("_id")
        return data
