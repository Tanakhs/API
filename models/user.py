from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from .objectid import PydanticObjectId


class Religion(Enum):
    JEWISH = "jewish"
    MUSLIM = "muslim"
    CHRISTIAN = "christian"
    ATHEIST = "atheist"


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Role(Enum):
    DEFAULT = "default"
    ADMIN = "admin"


class User(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    name: str
    given_name: str
    family_name: str
    picture: str
    email: str
    age: Optional[int]
    gender: Gender = Gender.OTHER
    religion: Religion = Religion.JEWISH
    date_added: Optional[datetime] = datetime.now()
    role: Role = Role.DEFAULT

    def to_json(self):
        return self.json()

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        data["gender"] = data["gender"].value
        data["religion"] = data["religion"].value
        data["role"] = data["role"].value

        if "_id" in data and data["_id"] is None:
            data.pop("_id")
        return data
