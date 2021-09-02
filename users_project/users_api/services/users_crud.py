from typing import Dict

from ..models import User, db
from ..schemas import UserSchema


def create_new_user(data: dict) -> Dict:
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    is_superuser = data.get('is_superuser')
    created_at = data.get('created_at')
    updated_at = data.get('updated_at')

    validation_errors = UserSchema().validate(data)

    if not validation_errors:
        new_user = User.create_user(email, first_name, last_name, created_at, updated_at, is_superuser)

        dump_user_schema = UserSchema().dump(new_user)

        return {'user': dump_user_schema, 'status_code': 201}

    return {'errors': validation_errors, 'status_code': 400}


def update_user(data: dict, user_id: int) -> Dict:
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    is_superuser_default = False
    is_superuser = data.get('is_superuser', is_superuser_default)

    user = User.get_user_by_id(user_id)

    email_check = User.get_user_by_email(email)

    if email_check is None or user.email == email:
        validation_errors = UserSchema().validate(data)

        if not validation_errors:
            updated_user = User.update_user(user, email, first_name, last_name, is_superuser)

            dump_user_schema = UserSchema().dump(updated_user)

            return {'user': dump_user_schema, 'status_code': 201}
        else:
            return {'errors': validation_errors, 'status_code': 400}

    else:
        return {'message': 'This email already exists', 'status_code': 409}


def remove_user(user_id: int) -> User or None:
    if User.query.filter_by(id=user_id):
        deleted_user = User.query.filter_by(id=user_id).delete()
        db.session.commit()

        return deleted_user

    return None
