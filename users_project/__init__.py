import os

from flask import Flask
from celery import Celery
from flask_caching import Cache

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

app = Flask(__name__)
app.config.from_pyfile('config.py')

celery = Celery('users_project', broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

cache = Cache(app)

from . import config
from users_project.auth_api.views import auth_bp
from users_project.users_api.views import user_bp
from users_project.users_api import models

app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)
