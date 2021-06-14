from flask import Flask
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:1234@localhost:5432"

from .models import db

migrate = Migrate(app, db)


def run_app(debug=False):
    app.run(debug=debug)