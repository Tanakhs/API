from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from bson.objectid import ObjectId

from models.chapter import Chapter
from models.chapter_update import ChapterUpdate
from models.comment import Comment
from models.objectid import PydanticObjectId
from models.user import User, verify_password, Role
from flask_cors import CORS
from flask_caching import Cache

from db_services import get_db_controller
from app_utils import permission_required

APP = Flask(__name__)
APP.config.from_object('config.Config')

CACHE = Cache(APP)

CORS(APP)
JWT = JWTManager(APP)

DB_NAME = 'secular_review'
CHAPTERS_COLLECTION_NAME = 'chapters'
USERS_COLLECTION = 'users'
DB_CONTROLLER = get_db_controller()


@APP.route('/api/v1/signup', methods=['POST'])
def signup():
    new_user = request.get_json()  # store the json body request
    new_user['role'] = "default"

    user_from_db = DB_CONTROLLER.find_one(DB_NAME, USERS_COLLECTION,
                                          {'user_name': new_user['user_name']})  # check if user exist
    if not user_from_db:
        user_model = User(**new_user)
        DB_CONTROLLER.insert_one(DB_NAME, USERS_COLLECTION, user_model.to_bson())
        return jsonify({'msg': 'User created successfully'}), 201
    else:
        return jsonify({'msg': 'Username already exists'}), 409


@APP.route('/api/v1/login', methods=['POST'])
def login():
    login_details = request.get_json()  # store the json body request
    user_from_db = DB_CONTROLLER.find_one(DB_NAME, USERS_COLLECTION,
                                          {'user_name': login_details['user_name']})  # search for user in database

    if user_from_db:

        if verify_password(user_from_db['password'], login_details['password']):
            access_token = create_access_token(identity=user_from_db['user_name'])  # create jwt token
            return jsonify(access_token=access_token), 200

    return jsonify({'msg': 'The username or password is incorrect'}), 401


@APP.route('/api/v1/chapters', methods=['GET'])
@CACHE.cached(timeout=30, query_string=True)
def get_chapters():
    records = []
    result = DB_CONTROLLER.find(DB_NAME, CHAPTERS_COLLECTION_NAME, {})
    for record in result:
        chapter = Chapter(**record)
        records.append(chapter.to_json())
    return records, 200


@APP.route('/api/v1/chapter/<string:chapter_id>', methods=['GET'])
def get_chapter(chapter_id):
    result = DB_CONTROLLER.find_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {'_id': ObjectId(chapter_id)})
    if result:
        result['_id'] = ObjectId(result['_id'])
        chapter = Chapter(**result)
        return chapter.to_json(), 200
    return jsonify({'msg': f'Chapter with chapter_id {chapter_id} not found', '_id': chapter_id}), 404


@APP.route('/api/v1/chapter/<string:chapter_id>', methods=['PUT'])
@permission_required(Role.ADMIN)
def update_chapter(chapter_id):
    updated_chapter = ChapterUpdate(**request.get_json())
    result = DB_CONTROLLER.update_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {'_id': ObjectId(chapter_id)},
                                      {'$set': updated_chapter.to_bson()})
    if result.matched_count == 0:
        return jsonify({'msg': f'Chapter with chapter_id {chapter_id} not found', '_id': chapter_id}), 404
    return jsonify({'msg': 'Chapter updated successfully'}), 202


@APP.route('/api/v1/chapter', methods=['POST'])
@permission_required(Role.ADMIN)
def post_chapter():
    chapter = Chapter(**request.get_json())
    result = DB_CONTROLLER.insert_one(DB_NAME, CHAPTERS_COLLECTION_NAME, chapter.to_bson())
    if result:
        return jsonify({'msg': 'Chapter created successfully', '_id': str(result)}), 201
    return jsonify({'msg': 'Chapter could not be created'}), 500


@APP.route('/api/v1/comment/<string:chapter_id>', methods=['POST'])
@permission_required(Role.DEFAULT)
def post_comment(current_user, chapter_id):
    new_comment = request.get_json()
    new_comment['_id'] = PydanticObjectId()
    new_comment['user_name'] = current_user.user_name
    new_comment['profile_picture_url'] = current_user.profile_picture_url
    comment = Comment(**new_comment)
    result = DB_CONTROLLER.update_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {'_id': ObjectId(chapter_id)},
                                      {'$push': {'comments': comment.to_bson()}})

    if result.matched_count == 0:
        return jsonify({'msg': f'Chapter with chapter_id {chapter_id} not found', '_id': chapter_id}), 404
    return jsonify({'msg': 'Post created successfully', '_id': str(comment.id)}), 202


@APP.route('/api/v1/comment/<string:chapter_id>/<string:comment_id>', methods=['PUT'])
@permission_required(Role.DEFAULT)
def update_comment(current_user, chapter_id, comment_id):
    chapter = DB_CONTROLLER.find_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {"_id": ObjectId(chapter_id)})
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

    result = DB_CONTROLLER.update_one(DB_NAME, CHAPTERS_COLLECTION_NAME, {"_id": ObjectId(chapter_id)},
                                      {"$set": {"comments": comments}})

    if result.modified_count == 0:
        return jsonify(
            {
                'msg': f'Update comment with comment_id {comment_id} and user name {current_user.user_name} failed'}), 404
    return jsonify({'msg': 'Comment updated successfully'}), 202


@APP.route('/api/v1/comment/<string:chapter_id>/<string:comment_id>', methods=['DELETE'])
@permission_required(Role.DEFAULT)
def delete_comment(current_user, chapter_id, comment_id):
    query = {"_id": ObjectId(chapter_id), "comments._id": ObjectId(comment_id),
             "comments.user_name": current_user.user_name}
    update = {"$pull": {"comments": {"_id": ObjectId(comment_id), "user_name": current_user.user_name}}}
    result = DB_CONTROLLER.update_one(DB_NAME, CHAPTERS_COLLECTION_NAME, query, update)
    if result.modified_count == 0:
        return jsonify(
            {
                'msg': f'deleting comment with comment_id {comment_id} and user name '
                       f'{current_user.user_name} under chapter with chapter_id {chapter_id} failed'}), 404
    return jsonify({'msg': 'Comment deleted successfully'}), 202


if __name__ == '__main__':
    APP.run(debug=True, host='0.0.0.0')
