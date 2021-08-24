import datetime
import random
import string

import jwt
from flask import request, jsonify, Blueprint

from users_project import cache
from users_project.config import SECRET_KEY, LOGIN_URL_LIFETIME, ACCESS_TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME
from users_project.users_api.models import User
from users_project.users_api.schemas import UserSchema
from users_project.utils import token_required, encode_auth_token
from users_project.validators import validate_email
from .tasks import async_auth_email

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/logout', methods=['POST'])
@token_required(only_superuser=False)
def logout(current_user):
    auth_token = None
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    try:
        refresh_auth_token = request.json.get('refresh')
    except AttributeError:
        return jsonify({'message': 'Provide refresh token for logout'}), 400

    decode_refresh_token = jwt.decode(refresh_auth_token, SECRET_KEY, algorithms=["HS256"])
    decode_access_token = jwt.decode(auth_token, SECRET_KEY, algorithms=["HS256"])
    if auth_token and refresh_auth_token and decode_refresh_token['user_id'] == decode_access_token['user_id']:
        if isinstance(auth_token, str):
            # mark the token as blacklisted
            cache.set(auth_token, "blacklist")
            cache.set(refresh_auth_token, "blacklist")
            return jsonify({'message': 'Successfully logged out.'}), 200
        else:
            return jsonify({'message': 'Fail'}), 400
    else:
        return jsonify({'message': 'Provide a valid access and refresh tokens.'}), 400


@auth_bp.route('/refresh-token', methods=['POST'])
@token_required(only_superuser=False)
def refresh_auth_token(current_user):
    try:
        refresh_token = request.json.get('refresh')
    except jwt.exceptions.DecodeError:
        return jsonify({'message': 'Invalid refresh token'}), 400

    access_token = request.headers.get('Authorization')
    if access_token:
        access_token = access_token.split(" ")[1]

    if refresh_token and not cache.get(refresh_token) == "blacklist":
        decode_refresh_token = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])
        decode_access_token = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
        if decode_refresh_token['user_id'] == decode_access_token['user_id']:
            result_access_token = encode_auth_token(current_user.id, ACCESS_TOKEN_LIFETIME)
            cache.set(access_token, "blacklist")

            current_user = UserSchema().dump(current_user)

            return jsonify({'access token': result_access_token,
                            'user': current_user}), 201

        return jsonify({'message': 'Invalid credentials'}), 400

    return jsonify({'message': 'Valid refresh token not provided'}), 401


@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.json['email']

    if not validate_email(email):
        return jsonify({'Bad Request': 'Enter a valid email'}), 400

    user = User.query.filter_by(email=email).first()

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
            return jsonify({'message': str(e)}), 400

        cache.set(url_token, login_code, LOGIN_URL_LIFETIME * 60)

        return jsonify({'message': f'Email sent successfully!',
                        'login url': f'{request.host_url}auth/{url_token}/login'}), 200

    return jsonify({'Not Found': 'User with this email not found'}), 404


@auth_bp.route('<login_url>/login', methods=['POST'])
def confirm_login(login_url):
    user_login_code = request.json.get('code')
    current_user = None

    try:
        login_code = cache.get(login_url)
        login_url_decode = jwt.decode(login_url, SECRET_KEY, algorithms=["HS256"])
        current_user = User.query.filter_by(id=login_url_decode['user_id']).first()
    except jwt.exceptions.ExpiredSignatureError:
        return jsonify({'message': 'Your login url expired, login again'}), 400
    except jwt.exceptions.InvalidTokenError:
        return jsonify({'message': 'Invalid login url.'}), 400

    if current_user and login_code and user_login_code.lower() == login_code.lower():
        access_token = encode_auth_token(current_user.id, ACCESS_TOKEN_LIFETIME)
        refresh_token = encode_auth_token(current_user.id, REFRESH_TOKEN_LIFETIME)

        users_schema = UserSchema()
        current_user = users_schema.dump(current_user)

        cache.delete(login_url)

        return jsonify({'access token': access_token,
                        'refresh_token': refresh_token,
                        'user': current_user})

    return jsonify({'message': 'Invalid credentials'})
