from users_project import app
from flask_marshmallow import Marshmallow
from .models import User

ma = Marshmallow(app)


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'created_at', 'updated_at', 'is_superuser')
        load_instance = True

    created_at = ma.auto_field(dump_only=True)
    updated_at = ma.auto_field(dump_only=True)


