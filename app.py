from flask import Flask

from controller.FileSystem import *
from controller.index import *


class Config(object):
    JOBS = []


app = Flask(__name__, template_folder='templates', static_url_path='/', static_folder='static')
app.config.from_object(Config())

app.register_blueprint(index)

app.register_blueprint(file)
