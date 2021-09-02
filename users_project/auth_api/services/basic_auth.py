import datetime
import random
import string

import jwt
from flask import request, jsonify

from users_project import cache
from users_project.auth_api.tasks import async_auth_email
from users_project.config import SECRET_KEY, LOGIN_URL_LIFETIME, ACCESS_TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME
from users_project.users_api.models import User
from users_project.users_api.schemas import UserSchema
from users_project.utils import encode_auth_token, get_user_access_token_from_headers, token_to_blacklist
from users_project.validators import validate_email


def get_user_tokens():
    try:
        refresh_auth_token = request.json.get('refresh')
    except AttributeError:
        return jsonify({'message': 'Provide refresh token for logout'}), 400
    auth_token = get_user_access_token_from_headers()

    return {'refresh': refresh_auth_token, 'access': auth_token}


def login_action(email: str) -> dict:
    if not validate_email(email):
        return {'message': 'Enter a valid email', 'status_code': 400}

    user = User.get_user_by_email(email)

    if user:

        login_code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
        async_auth_email.delay(login_code, user.id, request.host_url, request.headers.get('User-Agent'))
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=LOGIN_URL_LIFETIME),
                'user_id': user.id
            }
            url_token = jwt.encode(
                payload,
                SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return {'message': str(e), 'status_code': 400}

        cache.set(url_token, login_code, LOGIN_URL_LIFETIME * 60)

        return {'message': f'Email sent successfully!',
                'login_url': f'{request.host_url}auth/{url_token}/login', 'status_code': 201}

    return {'message': 'User with this email not found', 'status_code': 404}


def confirm_login_action(login_url: str, user_login_code: str) -> dict:
    current_user = None

    try:
        login_code = cache.get(login_url)
        login_url_decode = jwt.decode(login_url, SECRET_KEY, algorithms=["HS256"])
        current_user = User.query.filter_by(id=login_url_decode['user_id']).first()
    except jwt.exceptions.ExpiredSignatureError:
        return {'message': 'Your token expired, please login again', 'status_code': 401}
    except jwt.exceptions.InvalidTokenError:
        return {'message': 'Invalid token. Please login again', 'status_code': 401}

    if current_user and login_code and user_login_code.lower() == login_code.lower():
        access_token = encode_auth_token(current_user.id, ACCESS_TOKEN_LIFETIME, refresh_token=False)
        refresh_token = encode_auth_token(current_user.id, REFRESH_TOKEN_LIFETIME, refresh_token=True)

        users_schema = UserSchema()
        current_user = users_schema.dump(current_user)

        cache.delete(login_url)

        return {'access_token': access_token,
                'refresh_token': refresh_token,
                'user': current_user, 'status_code': 200}


def logout_action() -> dict:
    users_tokens = get_user_tokens()
    try:
        decode_refresh_token = jwt.decode(users_tokens['refresh'], SECRET_KEY, algorithms=["HS256"])
    except jwt.exceptions.ExpiredSignatureError:
        return {'message': 'Your token expired, please login again', 'status_code': 401}
    except jwt.exceptions.InvalidTokenError:
        return {'message': 'Invalid token. Please login again', 'status_code': 401}

    decode_access_token = jwt.decode(users_tokens['access'], SECRET_KEY, algorithms=["HS256"])
    if users_tokens['access'] and users_tokens['refresh'] and \
            decode_refresh_token['user_id'] == decode_access_token['user_id']:

        # mark the token as blacklisted
        token_to_blacklist(users_tokens['access'])
        token_to_blacklist(users_tokens['refresh'])
        return {'message': 'Successfully logged out.', 'status_code': 200}
    else:
        return {'message': 'Provide a valid access and refresh tokens.', 'status_code': 400}
