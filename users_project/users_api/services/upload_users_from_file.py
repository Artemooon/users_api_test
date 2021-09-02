from typing import List, Dict

from ..models import User
from ..schemas import UserSchema


def upload_users_from_json(file_data: List[Dict]) -> Dict:
    results = {}
    users_email_exists = []
    users_email_invalid = []
    users_created = []

    for user in file_data:
        validation_errors = None
        if User.get_user_by_email(user['email']) is None:
            validation_errors = UserSchema().validate(user)

            if not validation_errors:
                User.create_user(user.get('email'), user.get('first_name'), user.get('last_name'),
                                 user.get('created_at'), user.get('updated_at'), user.get('is_superuser', False))

                users_created.append(f'{user["email"]} successfully created')
                results['Users successfully created'] = users_created

            else:
                users_email_invalid.append(f'{user["email"]} {validation_errors}')
                results['Bad request'] = users_email_invalid

        elif User.get_user_by_email(user['email']):
            users_email_exists.append(f'{user["email"]} email already exists')
            results['Already exists'] = users_email_exists

    return results
