from flask import Flask
from pymongo import MongoClient
from .db_services.mongodb_service import MongodbService
from .db_services.db_controller import DbController

app = Flask(__name__)

DB_NAME = "SecularReview"
CHAPTERS_COLLECTION_NAME = "chapters"


def get_db_controller():
    client = MongoClient('localhost', 27017)
    mongo_db_service = MongodbService(client)
    db_controller = DbController(mongo_db_service)
    return db_controller


db_controller = get_db_controller()


@app.route('/api/v1/chapters', methods=["GET"])
def get_chapters():
    db_name = DB_NAME
    collection_name = CHAPTERS_COLLECTION_NAME
    db_controller.find_many(db_name, collection_name, " ")
    return


@app.route('/api/v1/chapter', methods=["GET"])
def get_chapter(name):
    db_name = DB_NAME
    collection_name = name
    db_controller.find_one(db_name, collection_name, " ")
    return
