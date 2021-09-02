from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('app.config.Configuration')
db = SQLAlchemy(app)
api = Api(app)


from . import models
from . import resouces


migrate = Migrate(app, db)

def run_app():
    app.run(host='localhost')