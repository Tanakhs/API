import functools
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import abort
from inspect import getfullargspec

from config import DB_NAME, USERS_COLLECTION
from models.user import User, Role


class PermissionRequired:
    def __init__(self, permission):
        self.permission = permission

    def __call__(self, function):
        @jwt_required()
        @functools.wraps(function)
        def wrapped_function(*args, **kwargs):
            from app import DB_CONTROLLER

            current_email = get_jwt_identity()
            user_from_db = DB_CONTROLLER.find_one(DB_NAME, USERS_COLLECTION, {'email': current_email})

            if not user_from_db:
                abort(401)
            user_model = User(**user_from_db)

            if not (user_model.role == self.permission or user_model.role == Role.ADMIN):
                abort(403)

            if 'current_user' in getfullargspec(function).args:
                kwargs['current_user'] = user_model
            return function(*args, **kwargs)

        return wrapped_function
