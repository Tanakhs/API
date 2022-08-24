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
    db_controller.find(DB_NAME, CHAPTERS_COLLECTION_NAME, {})
    return


@app.route('/api/v1/chapter/<string:chapter_id>', methods=["GET"])
def get_chapter(chapter_id):
    db_controller.find_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {"_id": chapter_id})
    return
