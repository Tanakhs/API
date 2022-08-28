from db_services.db_service_interface import IDbService
from bson.objectid import ObjectId


class DbController:
    def __init__(self, db_service: IDbService):
        self._db_service = db_service

    def find_one(self, db_name: str, collection_name: str, query: dict) -> dict:
        return self._db_service.find_one(db_name, collection_name, query)

    def find(self, db_name: str, collection_name: str, query: dict) -> dict:
        return self._db_service.find(db_name, collection_name, query)

    def insert_one(self, db_name: str, collection_name: str, record: dict) -> ObjectId:
        return self._db_service.insert_one(db_name, collection_name, record)

    def update_one(self, db_name: str, collection_name: str, record_id, record: dict) -> str:
        self._db_service.update_one(db_name, collection_name, record_id, record)

    def delete_one(self, db_name: str, collection_name: str, record_id) -> str:
        self._db_service.delete_one(db_name, collection_name, record_id)
