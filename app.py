import hashlib
import datetime
import os
from functools import wraps
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from db_services.mongodb_service import MongodbService
from db_services.db_controller import DbController
from bson.objectid import ObjectId

from models.chapter import Chapter
from models.chapter_update import ChapterUpdate
from models.comment import Comment
from models.objectid import PydanticObjectId
from models.user import User, verify_password, Role
from flask_cors import CORS
from flask_caching import Cache

app = Flask(__name__)
# app.config.from_object(Config)  # Set the configuration variables to the flask application
cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})

CORS(app)
jwt = JWTManager(app)

DB_NAME = 'secular_review'
CHAPTERS_COLLECTION_NAME = 'chapters'
USERS_COLLECTION = 'users'


def config():
    app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)


def get_db_controller():
    client = MongoClient('mongodb://localhost:27017/')
    mongo_db_service = MongodbService(client)
    db_controller = DbController(mongo_db_service)
    return db_controller


_db_controller = get_db_controller()


def token_required(f):
    @wraps(f)
    @jwt_required()
    def inner(*args, **kwargs):
        current_user = get_jwt_identity()  # Get the identity of the current user
        user_from_db = _db_controller.find_one(DB_NAME, USERS_COLLECTION, {'user_name': current_user})
        if user_from_db:
            user_model = User(**user_from_db)
            return f(user_model, *args, **kwargs)
        else:
            return jsonify({'msg': 'Profile not found'}), 401

    return inner


def admin_required(f):
    @wraps(f)
    @jwt_required()
    def inner(*args, **kwargs):
        current_user = get_jwt_identity()  # Get the identity of the current user
        user_from_db = _db_controller.find_one(DB_NAME, USERS_COLLECTION, {'user_name': current_user})
        if user_from_db and user_from_db['role'] == Role.ADMIN.value:
            user_model = User(**user_from_db)
            return f(user_model, *args, **kwargs)
        else:
            return jsonify({'msg': 'Admin permissions required'}), 403

    return inner


@app.route('/api/v1/signup', methods=['POST'])
def signup():
    new_user = request.get_json()  # store the json body request
    new_user['role'] = "default"
    user_from_db = _db_controller.find_one(DB_NAME, USERS_COLLECTION,
                                           {'user_name': new_user['user_name']})  # check if user exist
    if not user_from_db:
        user_model = User(**new_user)
        _db_controller.insert_one(DB_NAME, USERS_COLLECTION, user_model.to_bson())
        return jsonify({'msg': 'User created successfully'}), 201
    else:
        return jsonify({'msg': 'Username already exists'}), 409


@app.route('/api/v1/login', methods=['POST'])
def login():
    login_details = request.get_json()  # store the json body request
    user_from_db = _db_controller.find_one(DB_NAME, USERS_COLLECTION,
                                           {'user_name': login_details['user_name']})  # search for user in database

    if user_from_db:

        if verify_password(user_from_db['password'], login_details['password']):
            access_token = create_access_token(identity=user_from_db['user_name'])  # create jwt token
            return jsonify(access_token=access_token), 200

    return jsonify({'msg': 'The username or password is incorrect'}), 401


@app.route('/api/v1/chapters', methods=['GET'])
@cache.cached(timeout=30, query_string=True)
def get_chapters():
    records = []
    result = _db_controller.find(DB_NAME, CHAPTERS_COLLECTION_NAME, {})
    for record in result:
        chapter = Chapter(**record)
        records.append(chapter.to_json())
    return records, 200


@app.route('/api/v1/chapter/<string:chapter_id>', methods=['GET'])
@cache.cached(timeout=30, query_string=True)
def get_chapter(chapter_id):
    result = _db_controller.find_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {'_id': ObjectId(chapter_id)})
    if result:
        result['_id'] = ObjectId(result['_id'])
        chapter = Chapter(**result)
        return chapter.to_json(), 200
    return jsonify({'msg': f'Chapter with chapter_id {chapter_id} not found', '_id': chapter_id}), 404


@app.route('/api/v1/chapter/<string:chapter_id>', methods=['PUT'])
@admin_required
def update_chapter(current_user, chapter_id):
    updated_chapter = ChapterUpdate(**request.get_json())
    result = _db_controller.update_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {'_id': ObjectId(chapter_id)},
                                       {'$set': updated_chapter.to_bson()})
    if result.matched_count == 0:
        return jsonify({'msg': f'Chapter with chapter_id {chapter_id} not found', '_id': chapter_id}), 404
    return jsonify({'msg': 'Chapter updated successfully'}), 202


@app.route('/api/v1/chapter', methods=['POST'])
@admin_required
def post_chapter(current_user):
    chapter = Chapter(**request.get_json())
    result = _db_controller.insert_one(DB_NAME, CHAPTERS_COLLECTION_NAME, chapter.to_bson())
    if result:
        return jsonify({'msg': 'Chapter created successfully', '_id': str(result)}), 201
    return jsonify({'msg': 'Chapter could not be created'}), 500


@app.route('/api/v1/comment/<string:chapter_id>', methods=['POST'])
@token_required
def post_comment(current_user, chapter_id):
    new_comment = request.get_json()
    new_comment['_id'] = PydanticObjectId()
    new_comment['user_name'] = current_user.user_name
    new_comment['profile_picture_url'] = current_user.profile_picture_url
    comment = Comment(**new_comment)
    result = _db_controller.update_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {'_id': ObjectId(chapter_id)},
                                       {'$push': {'comments': comment.to_bson()}})

    if result.matched_count == 0:
        return jsonify({'msg': f'Chapter with chapter_id {chapter_id} not found', '_id': chapter_id}), 404
    return jsonify({'msg': 'Post created successfully'}), 202


@app.route('/api/v1/comment/<string:chapter_id>/<string:comment_id>', methods=['PUT'])
@token_required
def update_comment(current_user, chapter_id, comment_id):
    chapter = _db_controller.find_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {"_id": ObjectId(chapter_id)})
    if not chapter:
        return jsonify(
            {'msg': f'chapter with chapter_id {chapter_id} was not found',
             '_id': chapter_id}), 404

    # Find the comment in the chapter document
    comments = chapter.get("comments")
    comment_to_update = None
    for c in comments:
        if ObjectId(c["_id"]) == ObjectId(comment_id) and c["user_name"] == current_user.user_name:
            comment_to_update = c
            break

    # Check if the comment was found
    if not comment_to_update:
        return jsonify(
            {'msg': f'comment with comment_id {comment_id} or with username {current_user.user_name} was not found',
             '_id': chapter_id}), 404

    new_comment = request.get_json()
    new_comment['user_name'] = current_user.user_name
    new_comment['profile_picture_url'] = current_user.profile_picture_url
    new_comment = Comment(**new_comment)
    comment_to_update.update(new_comment.to_bson())
    # Replace the updated comment in the comments list
    comment_index = comments.index(comment_to_update)
    comments[comment_index] = comment_to_update

    result = _db_controller.update_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {"_id": ObjectId(chapter_id)},
                                       {"$set": {"comments": comments}})

    if result.modified_count == 0:
        return jsonify(
            {
                'msg': f'Update comment with comment_id {comment_id} and user name {current_user.user_name} failed'}), 404
    return jsonify({'msg': 'Comment updated successfully'}), 202


@app.route('/api/v1/comment/<string:chapter_id>/<string:comment_id>', methods=['DELETE'])
@token_required
def delete_comment(current_user, chapter_id, comment_id):
    query = {"_id": ObjectId(chapter_id), "comments._id": ObjectId(comment_id),
             "comments.user_name": current_user.user_name}
    update = {"$pull": {"comments": {"_id": ObjectId(comment_id), "user_name": current_user.user_name}}}
    result = _db_controller.update_one(DB_NAME, CHAPTERS_COLLECTION_NAME, query, update)
    if result.modified_count == 0:
        return jsonify(
            {
                'msg': f'deleting comment with comment_id {comment_id} and user name {current_user.user_name} under chapter with chapter_id {chapter_id} failed'}), 404
    return jsonify({'msg': 'Comment deleted successfully'}), 202


@app.route('/api/v1/user', methods=['GET'])
@token_required
def profile(current_user):
    return jsonify(current_user)


if __name__ == '__main__':
    config()
    app.run(debug=True)
