import jwt
from flask import request

from users_project import cache
from users_project.config import SECRET_KEY, ACCESS_TOKEN_LIFETIME
from users_project.users_api.models import User
from users_project.users_api.schemas import UserSchema
from users_project.utils import get_user_access_token_from_headers, encode_auth_token, token_to_blacklist


def refresh_access_token(current_user: User) -> dict:
    try:
        refresh_token = request.json.get('refresh')
    except jwt.exceptions.DecodeError:
        return {'message': 'Invalid refresh token', 'status_code': 400}

    access_token = get_user_access_token_from_headers()

    if not cache.get(refresh_token) == "blacklist":
        try:
            decode_refresh_token = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])
        except jwt.exceptions.ExpiredSignatureError:
            return {'message': 'Your token expired, please login again', 'status_code': 401}

        decode_access_token = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
        if decode_refresh_token['user_id'] == decode_access_token['user_id'] and \
                decode_refresh_token['typ'] == 'refresh':
            result_access_token = encode_auth_token(current_user.id, ACCESS_TOKEN_LIFETIME, refresh_token=True)
            token_to_blacklist(access_token)

            current_user = UserSchema().dump(current_user)

            return {'access_token': result_access_token,
                    'user': current_user,
                    'status_code': 201}

        return {'message': 'Invalid refresh token', 'status_code': 400}

    return {'message': 'Provided refresh token not found', 'status_code': 401}
