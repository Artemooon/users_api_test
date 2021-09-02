from flask import request, jsonify, Blueprint

from users_project.utils import token_required
from .services.basic_auth import logout_action, login_action, confirm_login_action
from .services.refresh_token import refresh_access_token

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/logout', methods=['POST'])
@token_required(only_superuser=False)
def logout_view(current_user):
    logout_response = logout_action()

    return jsonify(logout_response), logout_response['status_code']


@auth_bp.route('/refresh-token', methods=['POST'])
@token_required(only_superuser=False)
def refresh_auth_token_view(current_user):
    refresh_response = refresh_access_token(current_user)

    return jsonify(refresh_response), refresh_response['status_code']


@auth_bp.route('/login', methods=['POST'])
def login_view():
    email = request.json['email']

    login_response = login_action(email)

    return jsonify(login_response), login_response['status_code']


@auth_bp.route('<login_url>/login', methods=['POST'])
def confirm_login_view(login_url):
    user_login_code = request.json.get('code')

    confirm_login_response = confirm_login_action(login_url, user_login_code)

    return jsonify(confirm_login_response), confirm_login_response['status_code']
