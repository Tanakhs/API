import hashlib
import datetime
from functools import wraps

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from db_services.mongodb_service import MongodbService
from db_services.db_controller import DbController

app = Flask(__name__)
jwt = JWTManager(app)

with open('.jwt_secret_key') as f:
    lines = f.readlines()
app.config['JWT_SECRET_KEY'] = str(lines)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

DB_NAME = "SecularReview"
CHAPTERS_COLLECTION_NAME = "chapters"
USERS_COLLECTION = "users"


def get_db_controller():
    client = MongoClient("mongodb://localhost:27017/")
    mongo_db_service = MongodbService(client)
    db_controller = DbController(mongo_db_service)
    return db_controller


_db_controller = get_db_controller()


def token_required(f):
    @wraps(f)
    @jwt_required()
    def inner(*args, **kwargs):
        current_user = get_jwt_identity()  # Get the identity of the current user
        user_from_db = _db_controller.find_one(DB_NAME, USERS_COLLECTION, {"username": current_user})
        if user_from_db:
            return f(current_user, *args, **kwargs)
        else:
            return jsonify({'msg': 'Profile not found'}), 404

    return inner


def admin_required(f):
    @wraps(f)
    @jwt_required()
    def inner(*args, **kwargs):
        current_user = get_jwt_identity()  # Get the identity of the current user
        user_from_db = _db_controller.find_one(DB_NAME, USERS_COLLECTION, {"username": current_user})
        if user_from_db and user_from_db["role"] == "admin":
            return f(current_user, *args, **kwargs)
        else:
            return jsonify({'msg': 'Admin permissions required'}), 404

    return inner


@app.route("/api/v1/signup", methods=["POST"])
def signup():
    new_user = request.get_json()  # store the json body request
    new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest()  # encrypt password
    doc = _db_controller.find_one(DB_NAME, USERS_COLLECTION, {"username": new_user["username"]})  # check if user exist
    if not doc:
        _db_controller.insert_one("SecularReview", "users", new_user)
        return jsonify({'msg': 'User created successfully'}), 201
    else:
        return jsonify({'msg': 'Username already exists'}), 409


@app.route("/api/v1/login", methods=["POST"])
def login():
    login_details = request.get_json()  # store the json body request
    user_from_db = _db_controller.find_one(DB_NAME, USERS_COLLECTION,
                                           {"username": login_details["username"]})  # search for user in database

    if user_from_db:
        encrypted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
        if encrypted_password == user_from_db['password']:
            access_token = create_access_token(identity=user_from_db['username'])  # create jwt token
            return jsonify(access_token=access_token), 200

    return jsonify({'msg': 'The username or password is incorrect'}), 401


@app.route('/api/v1/chapters', methods=["GET"])
def get_chapters():
    _db_controller.find(DB_NAME, CHAPTERS_COLLECTION_NAME, {})
    return


@app.route('/api/v1/chapter/<string:chapter_id>', methods=["GET"])
def get_chapter(chapter_id):
    _db_controller.find_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {"_id": chapter_id})
    return


@app.route("/api/v1/user", methods=["GET"])
@admin_required
def profile(current_user):
    return jsonify(current_user)


if __name__ == '__main__':
    app.run(debug=True)
