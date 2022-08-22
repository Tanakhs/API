from flask import Flask
from pymongo import MongoClient
from .db_services.mongodb_service import MongodbService
from .db_services.db_controller import DbController

app = Flask(__name__)


def get_db_controller():
    client = MongoClient('localhost', 27017)
    mongo_db_service = MongodbService(client)
    db_controller = DbController(mongo_db_service)
    return db_controller


db_controller = get_db_controller()


@app.route('/')
def home():
    return 'Home'


@app.route('/api/v1/chapters')
def get_chapters():
    db_name = "SecularReview"
    collection_name = "chapters"
    query = "{}"
    db_controller.find_many(db_name, collection_name, query)
    return

@app.route('/api/v1/chapter')
def get_chapter(name):
    db_name = "SecularReview"
    collection_name = name
    query = "{}"
    db_controller.find_one(db_name, collection_name, query)
    return
