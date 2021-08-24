from datetime import datetime, timedelta
from functools import wraps, update_wrapper
from users_project import cache

from flask import request, jsonify
from users_project.users_api.models import User
from users_project import app
import jwt


def check_token_blacklist(auth_token: str) -> bool:
    # check whether auth token has been blacklisted
    token = cache.get(auth_token)
    if token == 'blacklist':
        return True

    return False


def token_required(only_superuser):
    def outer(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_token = None

            auth_header = 'Authorization'
            if auth_header in request.headers:
                auth_token = request.headers['Authorization'].split(' ')[1]
            if not auth_token:
                return jsonify({'Unauthorized': 'Token is missing'}), 401

            if check_token_blacklist(auth_token) is True:
                return jsonify({'Not found': 'Token is in a blacklist, login again'}), 404

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


def encode_auth_token(user_id: int, exp: float):

    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(minutes=exp),
            'iat': datetime.utcnow(),
            'user_id': user_id
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return jsonify({'message': str(e)}), 400
