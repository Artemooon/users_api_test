from flask_mail import Mail, Message

from users_project import app
from users_project import celery
from users_project.users_api.models import User

mail = Mail(app)


@celery.task
def async_auth_email(code: str, user_id: int, site_domain: str, device_data: str) -> None:
    with app.app_context():
        current_user = User.query.filter_by(id=user_id).first()
        msg = Message(subject=f"Login code on {site_domain}", sender='artem.logachov773@gmail.com',
                      recipients=[current_user.email])
        msg.body = f"""
                    <b>Hi, {current_user.first_name}</b>
                    <p>To complete the login, enter the verification code below.</p>
                    <span>Login code: <b>{code}</b></span>
                    <span>Device: {device_data}</span>
                    <p>If you think, it's not you, then just ignore this email.</p>
                    """
        mail.send(msg)
