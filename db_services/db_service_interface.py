from abc import abstractmethod
from pymongo.results import UpdateResult, DeleteResult
from bson.objectid import ObjectId


class IDbService:

    @abstractmethod
    def find_one(self, db_name: str, collection_name: str, query: dict) -> dict: raise NotImplementedError

    @abstractmethod
    def find(self, db_name: str, collection_name: str, query: dict) -> dict: raise NotImplementedError

    @abstractmethod
    def insert_one(self, db_name: str, collection_name: str, record: dict) -> ObjectId: raise NotImplementedError

    @abstractmethod
    def update_one(self, db_name: str, collection_name: str, query: dict,
                   record: dict, array_filters: list = []) -> UpdateResult: raise NotImplementedError

    @abstractmethod
    def delete_one(self, db_name: str, collection_name: str, query: dict) -> DeleteResult: raise NotImplementedError
