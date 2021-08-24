import datetime

from flask import request, jsonify, json, Blueprint

from .models import User
from .schemas import UserSchema
from users_project.utils import token_required
from users_project.validators import validate_email

user_bp = Blueprint('users', __name__, url_prefix='/users')


@user_bp.route('/delete-user/<int:_id>', methods=['DELETE'])
@token_required(only_superuser=True)
def delete_user(current_user, _id):
    if User.query.filter_by(id=_id).first():
        User.remove_user(_id)

        return jsonify({'Success': 'User successfully deleted'}), 200

    return jsonify({'Not found': 'User with provided id not found'}), 404


@user_bp.route('/update-user/<int:_id>', methods=['PATCH'])
@token_required(only_superuser=True)
def update_user(_id):
    if User.query.filter_by(id=_id):
        user = User.get_user_by_id(_id)

    try:
        email = request.json['email']
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        default_datetime = datetime.datetime.utcnow()
        default_datetime = default_datetime.isoformat()
        created_at = request.json['updated_at'] or json.dumps(default_datetime)
    except KeyError as ke:
        return jsonify({"Bad request": f"Invalid provided data for {ke}"}), 400

    email_check = User.query.filter_by(email=email).first()

    if validate_email(email) and (email_check is None or user.email == email):
        try:
            patched_user = User.update_user(user, email, first_name, last_name, created_at)

            dump_user_schema = UserSchema().dump(patched_user)

            return jsonify(dump_user_schema), 200
        except Exception as e:
            return jsonify({'Bad Request': str(e)}), 400

    elif email_check:
        return jsonify({"Already Exists": "This email already exists"}), 409

    else:
        return jsonify({"Bad request": "Invalid email"}), 400


@user_bp.route('/get-user/<int:_id>', methods=['GET'])
@token_required(only_superuser=False)
def get_user_by_id(current_user, _id):
    user = User.get_user_by_id(_id)
    dump_users_schema = UserSchema().dump(user)

    return jsonify(dump_users_schema), 200


@user_bp.route('/get-all-users', methods=['GET'])
@token_required(only_superuser=False)
def get_all_users(current_user):

    users_schema = UserSchema(many=True)
    dump_users_schema = users_schema.dump(User.get_all_users())

    return jsonify(dump_users_schema), 200


@user_bp.route('/create-user', methods=['POST'])
@token_required(only_superuser=True)
def create_user(current_user):
    data = request.get_json()
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    is_superuser = data.get('is_superuser')
    default_datetime = datetime.datetime.utcnow()
    default_datetime = default_datetime.isoformat()
    created_at = data.get('created_at', json.dumps(default_datetime))
    updated_at = data.get('updated_at', json.dumps(default_datetime))

    if validate_email(email) and User.query.filter_by(email=email).first() is None:
        if first_name and last_name:
            try:
                new_user = User.create_user(email, first_name, last_name, created_at, updated_at, is_superuser)

                dump_user_schema = UserSchema().dump(new_user)

                return jsonify(dump_user_schema), 201
            except Exception as e:
                return jsonify({'Bad Request': str(e)}), 400

        else:
            return jsonify({"Bad request": "First name or last name not provided"}), 400

    elif User.query.filter_by(email=data.get('email')).first():
        return jsonify({"Already Exists": "This email already exists"}), 409

    else:
        return jsonify({"Bad request": "Invalid email"}), 400


@user_bp.route('/upload-users-file', methods=['POST'])
def get_users_from_file():
    try:
        file = request.files['file']
    except KeyError:
        return jsonify({'message': 'Json file not provided'}), 400

    if file.filename.split('.')[-1] == 'json':
        try:
            file_data = json.load(file)
        except Exception:
            return jsonify({'message': 'Invalid json file format'}), 400
    else:
        return jsonify({'message': 'Only json files'}), 415

    results = {}
    users_email_exists = []
    users_email_invalid = []
    users_created = []
    default_datetime = datetime.datetime.utcnow()
    default_datetime = default_datetime.isoformat()
    for user in file_data:
        if validate_email(user['email']) and User.query.filter_by(email=user['email']).first() is None:
            try:
                User.create_user(email=user['email'], first_name=user['first_name'], last_name=user['last_name'],
                                 created_at=user.get('created_at', json.dumps(default_datetime)),
                                 updated_at=user.get('updated_at', json.dumps(default_datetime)))

                users_created.append(f'{user["email"]} successfully created')
                results['Users successfully created'] = users_created
            except Exception as e:
                return jsonify({'Bad Request': str(e)}), 400

        elif User.get_user_by_email(user['email']):
            users_email_exists.append(f'{user["email"]} email already exists')
            results['Already exists'] = users_email_exists

        else:
            users_email_invalid.append(f'{user["email"]} invalid email')
            results['Bad request'] = users_email_invalid

    return jsonify(results)

