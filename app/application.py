"""initiate main application variables.
create an flask object at the `app` variable, SQLAlchemy object an the `db` variable,
and flask_restful.api object at `api` variable."""

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('app.config.Configuration')
db = SQLAlchemy(app)
api = Api(app)


from . import models
from . import resouces


def run_app():
    """run app in the test localhost server."""
    app.run(host='localhost')