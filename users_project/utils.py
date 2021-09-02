from datetime import datetime, timedelta
from functools import wraps, update_wrapper

import jwt
from flask import request, jsonify

from users_project import app
from users_project import cache
from users_project.users_api.models import User


def check_token_blacklist(auth_token: str) -> bool:
    # check whether auth token has been blacklisted
    token = cache.get(auth_token)
    if token == 'blacklist':
        return True

    return False


def token_to_blacklist(token):
    cache.set(token, "blacklist")


def get_user_access_token_from_headers():
    auth_token = None

    auth_header = 'Authorization'
    if auth_header in request.headers:
        auth_token = request.headers[auth_header].split(' ')[1]
    if not auth_token:
        return jsonify({'Unauthorized': 'Token is missing'}), 401

    return auth_token


def token_required(only_superuser: bool):
    def outer(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_token = get_user_access_token_from_headers()

            if check_token_blacklist(auth_token) is True:
                return jsonify({'message': 'Token is in a blacklist, login again'}), 404

            try:
                data = jwt.decode(auth_token, app.config['SECRET_KEY'], algorithms=["HS256"])
                current_user = User.query.filter_by(id=data['user_id']).first()
                if not current_user:
                    return jsonify({'message': 'Authenticated user does not exists'}), 403
                if only_superuser and not current_user.is_superuser:
                    return jsonify({'message': 'This option allows only for superuser'}), 403
            except jwt.exceptions.ExpiredSignatureError:
                return jsonify({'message': 'Your token expired, please login again'}), 401
            except jwt.exceptions.InvalidTokenError:
                return jsonify({'message': 'Invalid token. Please login again'}), 401

            return func(current_user, *args, **kwargs)

        return update_wrapper(wrapper, func)

    return outer


def encode_auth_token(user_id: int, exp: float, refresh_token: bool):
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(minutes=exp),
            'iat': datetime.utcnow(),
            'typ': 'refresh' if refresh_token else 'access',
            'user_id': user_id
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return jsonify({'message': str(e)}), 400
