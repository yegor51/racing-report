from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:1234@localhost:5432"
api = Api(app)


from .models import db
from . import resouces

migrate = Migrate(app, db)


def run_app(debug=False):
    app.run(host='localhost')