from pymongo import MongoClient
from db_services.mongodb_service import MongodbService
from db_services.db_controller import DbController


def get_db_controller():
    client = MongoClient('mongodb://localhost:27017/')
    mongo_db_service = MongodbService(client)
    return DbController(mongo_db_service)
