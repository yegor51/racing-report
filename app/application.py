from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://test_user:1234@localhost:5432/test_db"
db = SQLAlchemy(app)
api = Api(app)


from . import models
from . import resouces


migrate = Migrate(app, db)

def run_app():
    app.run(host='localhost')