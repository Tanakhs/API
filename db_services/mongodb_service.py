from db_services.db_service_interface import IDbService
from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.results import UpdateResult, DeleteResult


class MongodbService(IDbService):

    def __init__(self, client: MongoClient):
        self._client = client

    def find_one(self, db_name: str, collection_name: str, query: dict) -> dict:
        collection = self.get_collection(db_name, collection_name)
        return collection.find_one(query)

    def find(self, db_name: str, collection_name: str, query: dict) -> dict:
        collection = self.get_collection(db_name, collection_name)
        return collection.find(query)

    def insert_one(self, db_name: str, collection_name: str, record: dict) -> ObjectId:
        collection = self.get_collection(db_name, collection_name)
        return collection.insert_one(record).inserted_id

    def update_one(self, db_name: str, collection_name: str, query: dict, record: dict,
                   array_filters: list = []) -> UpdateResult:
        collection = self.get_collection(db_name, collection_name)
        return collection.update_one(query, record, array_filters=array_filters)

    def delete_one(self, db_name: str, collection_name: str, query: dict) -> DeleteResult:
        collection = self.get_collection(db_name, collection_name)
        collection.delete_one(query)

    def get_collection(self, db_name: str, collection_name: str):
        if self.is_db_exist(db_name):
            if self.is_collection_exist(db_name, collection_name):
                return self._client[db_name][collection_name]
            raise KeyError(f'collection: {collection_name} does not exist under database: {db_name}')
        raise KeyError(f'database: {db_name} does not exist under client: {self._client}')

    def is_db_exist(self, db_name: str) -> bool:
        db_list = self._client.list_database_names()
        if db_name in db_list:
            return True
        return False

    def is_collection_exist(self, db_name: str, collection_name: str) -> bool:
        db = self._client[db_name]
        collection_list = db.list_collection_names()
        if collection_name in collection_list:
            return True
        return False
