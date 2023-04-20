import requests
from bson.objectid import ObjectId
from flask import Flask, request, jsonify
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token

from app_utils import PermissionRequired
from config import GOOGLE_CLIENT_ID, GOOGLE_SECRET_KEY, DB_NAME, USERS_COLLECTION, CHAPTERS_COLLECTION_NAME
from db_services import get_db_controller
from models.chapter import Chapter
from models.chapter_update import ChapterUpdate
from models.comment import Comment
from models.user import User, Role

APP = Flask(__name__)
APP.config.from_object('config.Config')

CACHE = Cache(APP)

CORS(APP)
JWT = JWTManager(APP)

DB_CONTROLLER = get_db_controller()


@APP.route('/api/v1/google_login', methods=['POST'])
def login():
    auth_code = request.get_json()['code']

    data = {
        'code': auth_code,
        'client_id': GOOGLE_CLIENT_ID,  # client ID
        'client_secret': GOOGLE_SECRET_KEY,  # client secret
        'redirect_uri': 'postmessage',
        'grant_type': 'authorization_code'
    }

    response = requests.post('https://oauth2.googleapis.com/token', data=data).json()
    headers = {
        'Authorization': f'Bearer {response["access_token"]}'
    }
    user_info = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers=headers).json()

    user_from_db = DB_CONTROLLER.find_one(DB_NAME, USERS_COLLECTION,
                                          {'email': user_info['email']})  # search for user in database

    if not user_from_db:
        user_model = User(**user_info)
        DB_CONTROLLER.insert_one(DB_NAME, USERS_COLLECTION, user_model.to_bson())

    jwt = create_access_token(identity=user_info['email'])  # create jwt token
    return jsonify(jwt=jwt, user=User(**user_info).to_json()), 200


@APP.route('/api/v1/chapters', methods=['GET'])
@CACHE.cached(timeout=30, query_string=True)
def get_chapters():
    all_chapters = DB_CONTROLLER.find(DB_NAME, CHAPTERS_COLLECTION_NAME)
    all_chapters = [Chapter(**chapter).to_json() for chapter in all_chapters]

    return all_chapters, 200


@APP.route('/api/v1/chapter/<string:chapter_id>', methods=['GET'])
def get_chapter(chapter_id):
    retrieved_chapter = DB_CONTROLLER.find_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {'_id': ObjectId(chapter_id)})
    if not retrieved_chapter:
        return jsonify({'msg': f'Chapter with chapter_id {chapter_id} was not found', '_id': chapter_id}), 404

    retrieved_chapter['_id'] = ObjectId(retrieved_chapter['_id'])
    chapter = Chapter(**retrieved_chapter)
    return chapter.to_json(), 200


@APP.route('/api/v1/chapter/<string:chapter_id>', methods=['PUT'])
@PermissionRequired(Role.ADMIN)
def update_chapter(chapter_id):
    try:
        updated_chapter = ChapterUpdate(**request.get_json())
    except Exception:
        return jsonify({'msg': 'Chapter is not in the correct schema'}), 400

    updated_result = DB_CONTROLLER.update_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {'_id': ObjectId(chapter_id)},
                                              {'$set': updated_chapter.to_bson()})

    if updated_result.matched_count == 0:
        return jsonify({'msg': f'Chapter with chapter_id {chapter_id} not found', '_id': chapter_id}), 404

    return jsonify({'msg': 'Chapter updated successfully'}), 202


@APP.route('/api/v1/chapter', methods=['POST'])
@PermissionRequired(Role.ADMIN)
def post_chapter():
    try:
        chapter = Chapter(**request.get_json())
    except Exception:
        return jsonify({'msg': 'Chapter is not in the correct schema'}), 400

    new_chapter_id = DB_CONTROLLER.insert_one(DB_NAME, CHAPTERS_COLLECTION_NAME, chapter.to_bson())

    if not new_chapter_id:
        return jsonify({'msg': 'Chapter could not be created'}), 500

    return jsonify({'msg': 'Chapter created successfully', '_id': str(new_chapter_id)}), 201


@APP.route('/api/v1/comment/<string:chapter_id>', methods=['POST'])
@PermissionRequired(Role.DEFAULT)
def post_comment(current_user, chapter_id):
    new_comment = request.get_json()
    new_comment['_id'] = ObjectId()
    new_comment['name'] = current_user.name
    new_comment['picture'] = current_user.picture

    try:
        comment = Comment(**new_comment)
    except Exception:
        return jsonify({'msg': 'Comment is not in the correct schema'}), 400

    update_result = DB_CONTROLLER.update_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {'_id': ObjectId(chapter_id)},
                                             {'$push': {'comments': comment.to_bson()}})

    if update_result.matched_count == 0:
        return jsonify({'msg': f'Chapter with chapter_id {chapter_id} not found', '_id': chapter_id}), 404

    return jsonify({'msg': 'Comment created successfully', '_id': str(comment.id)}), 202


@APP.route('/api/v1/comment/<string:chapter_id>/<string:comment_id>', methods=['PUT'])
@PermissionRequired(Role.DEFAULT)
def update_comment(current_user, chapter_id, comment_id):
    chapter = DB_CONTROLLER.find_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {"_id": ObjectId(chapter_id)})
    if not chapter:
        return jsonify(
            {'msg': f'chapter with chapter_id {chapter_id} was not found', '_id': chapter_id}), 404

    # Find the comment in the chapter document
    comments = chapter.get("comments")
    comment_to_update, comment_index = None, None
    for comment in comments:
        if ObjectId(comment["_id"]) == ObjectId(comment_id) and comment["name"] == current_user.name:
            comment_to_update = comment
            comment_index = comments.index(comment)
            break

    if not comment_to_update:
        return jsonify(
            {'msg': f'comment with comment_id {comment_id} or with username {current_user.name} was not found',
             '_id': chapter_id}), 404

    new_comment = request.get_json()
    new_comment['_id'] = comment_to_update['_id']
    new_comment['name'] = current_user.name
    new_comment['picture'] = current_user.picture

    try:
        new_comment = Comment(**new_comment)
    except Exception:
        return jsonify({'msg': 'New comment is not in the correct schema'}), 400

    # Replace the updated comment in the comments list
    comments[comment_index] = new_comment.to_bson()

    result = DB_CONTROLLER.update_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {"_id": ObjectId(chapter_id)},
                                      {"$set": {"comments": comments}})

    if result.modified_count == 0:
        return jsonify(
            {'msg': f'Update comment with comment_id {comment_id} and user name {current_user.name} failed'}), 404

    return jsonify({'msg': 'Comment updated successfully'}), 202


@APP.route('/api/v1/comment/<string:chapter_id>/<string:comment_id>', methods=['DELETE'])
@PermissionRequired(Role.DEFAULT)
def delete_comment(current_user, chapter_id, comment_id):
    comment_to_delete = {"_id": ObjectId(chapter_id), "comments._id": ObjectId(comment_id),
                         "comments.name": current_user.name}

    query_to_delete = {"$pull": {"comments": {"_id": ObjectId(comment_id), "name": current_user.name}}}

    result = DB_CONTROLLER.update_one(DB_NAME, CHAPTERS_COLLECTION_NAME, comment_to_delete, query_to_delete)

    if result.modified_count == 0:
        return jsonify(
            {
                'msg': f'deleting comment with comment_id {comment_id} and user name '
                       f'{current_user.name} under chapter with chapter_id {chapter_id} failed'}), 404

    return jsonify({'msg': 'Comment deleted successfully'}), 202


if __name__ == '__main__':
    APP.run(debug=True, host='0.0.0.0')
