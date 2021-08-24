from flask.cli import FlaskGroup

from users_project import app
from users_project.users_api.models import db, User

cli = FlaskGroup(app)


@cli.command("createdb")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    print('DB Successfully created')


@cli.command("createsuperuser")
def create_superuser():
    User.create_user(email='artiom.logachiov@gmail.com', first_name='Artem', last_name='Logachov', is_superuser=True,
                     created_at=None, updated_at=None)
    print('Superuser created')


if __name__ == "__main__":
    cli()
