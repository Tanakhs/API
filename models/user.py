import binascii
import hashlib
import os
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, SecretStr, validator
from typing import Optional
from datetime import datetime
from enum import Enum

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


def hash_password(password: SecretStr) -> SecretStr:
    """Hash a password for storing."""
    salt = b'__hash__' + hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.get_secret_value().encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def is_hash(pw: SecretStr) -> bool:
    return pw.get_secret_value().startswith('__hash__') and len(pw) == 200


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a stored password against one provided by user"""
    salt = stored_password[:72]
    stored_password = stored_password[72:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


class User(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    password: SecretStr
    user_name: str
    profile_picture_url: str
    email_address: str
    age: int
    gender: Gender = Gender.OTHER
    religion: Religion = Religion.JEWISH
    date_added: Optional[datetime] = datetime.now()
    role: Role = Role.DEFAULT

    @validator('password')
    def hash_password(cls, pw: SecretStr) -> SecretStr:
        if is_hash(pw):
            return pw
        return SecretStr(hash_password(pw))

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        data["gender"] = data["gender"].value
        data["religion"] = data["religion"].value
        data["role"] = data["role"].value
        data["password"] = data["password"].get_secret_value()

        if "_id" in data and data["_id"] is None:
            data.pop("_id")
        return data
