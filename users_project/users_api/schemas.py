from datetime import datetime
from marshmallow import Schema, fields
from marshmallow.validate import Length


class UserSchema(Schema):

    email = fields.Email(required=True, validate=Length(max=140))
    first_name = fields.String(required=True, validate=Length(min=2, max=100))
    last_name = fields.String(validate=Length(min=2, max=100))
    created_at = fields.DateTime(dump_only=True, default=datetime.utcnow())
    updated_at = fields.DateTime(dump_only=True, default=datetime.utcnow())
    is_superuser = fields.Boolean(default=False)

    class Meta:
        fields = ("id", "email", "first_name", "last_name", "created_at", "updated_at", "is_superuser")
        ordered = True


