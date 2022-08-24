from abc import abstractmethod


class IDbService:

    @abstractmethod
    def find_one(self, db_name: str, collection_name: str, query: str) -> dict: raise NotImplementedError

    @abstractmethod
    def find(self, db_name: str, collection_name: str, query: str) -> dict: raise NotImplementedError

    @abstractmethod
    def insert_one(self, db_name: str, collection_name: str, record: dict) -> str: raise NotImplementedError

    @abstractmethod
    def update_one(self, db_name: str, collection_name: str, record_id: str, record: dict): raise NotImplementedError

    @abstractmethod
    def delete_one(self, db_name: str, collection_name: str, record_id: str): raise NotImplementedError
