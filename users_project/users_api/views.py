from flask import request, jsonify, json, Blueprint

from users_project.utils import token_required
from .models import User
from .schemas import UserSchema
from .services.upload_users_from_file import upload_users_from_json
from .services.users_crud import remove_user, create_new_user, update_user

user_bp = Blueprint('users', __name__, url_prefix='/users')


@user_bp.route('/delete-user/<int:_id>', methods=['DELETE'])
@token_required(only_superuser=True)
def delete_user_view(current_user, _id):
    removed_user = remove_user(_id)
    if removed_user:
        return jsonify({'message': 'User successfully deleted', 'user': removed_user}), 200

    return jsonify({'Not found': 'User with provided id not found'}), 404


@user_bp.route('/update-user/<int:_id>', methods=['PATCH'])
@token_required(only_superuser=True)
def update_user_view(current_user, _id):
    data = request.get_json()

    updated_user_response = update_user(data, _id)

    return jsonify(updated_user_response), updated_user_response['status_code']


@user_bp.route('/get-user/<int:_id>', methods=['GET'])
@token_required(only_superuser=False)
def get_user_by_id_view(current_user, _id):
    user = User.get_user_by_id(_id)
    if user:
        dump_users_schema = UserSchema().dump(user)

        return jsonify(dump_users_schema), 200

    return jsonify({'message': 'User with provided id not found'}), 404


@user_bp.route('/get-all-users', methods=['GET'])
@token_required(only_superuser=False)
def get_all_users_view(current_user):
    users_schema = UserSchema(many=True)
    dump_users_schema = users_schema.dump(User.get_all_users())

    return jsonify(dump_users_schema), 200


@user_bp.route('/create-user', methods=['POST'])
@token_required(only_superuser=True)
def create_user_view(current_user):
    data = request.get_json()

    if User.get_user_by_email(data.get("email")) is None:
        created_user_response = create_new_user(data)

        return jsonify(created_user_response), created_user_response['status_code']

    return jsonify({"message": "This email already exists"}), 409


@user_bp.route('/upload-users-file', methods=['POST'])
@token_required(only_superuser=True)
def upload_users_from_file_view(current_user):
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

    uploaded_file_response = upload_users_from_json(file_data)

    return jsonify(uploaded_file_response)
