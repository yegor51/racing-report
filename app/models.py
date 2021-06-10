from application import app
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(app)


class GroupModel(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class StudentModel(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)


class CourseModel(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)