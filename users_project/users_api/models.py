from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from users_project import app

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True, index=True)
    email = db.Column(db.String(140), nullable=False, unique=True, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_superuser = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return '<User %r>' % self.first_name

    @staticmethod
    def create_user(email: str, first_name: str, last_name: str, created_at=None, updated_at=None,
                    is_superuser=False) -> 'User':
        new_user = User(email=email, first_name=first_name, last_name=last_name, created_at=created_at,
                        updated_at=updated_at, is_superuser=is_superuser)

        db.session.add(new_user)
        db.session.commit()

        return new_user

    @staticmethod
    def update_user(user: 'User', email: str, first_name: str, last_name: str,
                    is_superuser=False) -> 'User':
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.updated_at = datetime.utcnow()
        user.is_superuser = is_superuser

        db.session.commit()

        return user

    @staticmethod
    def get_all_users():
        return User.query.order_by(User.first_name).order_by(User.id.desc()).all()

    @staticmethod
    def get_user_by_id(_id: int) -> 'User' or None:
        return User.query.filter_by(id=_id).first() or None

    @staticmethod
    def get_user_by_email(email: str) -> 'User' or None:
        return User.query.filter_by(email=email).first() or None
