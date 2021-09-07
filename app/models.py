from .application import app, db
from flask_sqlalchemy import SQLAlchemy


class GroupModel(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name


students_courses_relation = db.Table('students_courses_relation',
                        db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True),
                        db.Column('student_id', db.Integer, db.ForeignKey('students.id'), primary_key=True)
                        )


class StudentModel(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    courses = db.relationship('CourseModel', secondary=students_courses_relation, lazy='subquery',
                              backref=db.backref('students', lazy=True))

    def __init__(self, group_id, first_name, last_name):
        self.group_id = group_id
        self.first_name = first_name
        self.last_name = last_name


class CourseModel(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    def __init__(self, name, description):
        self.name = name
        self.description = description


if not db.engine.table_names() or StudentModel.query.count() == 0:
    from app.create_test_data import create_test_data
    db.create_all()
    create_test_data()
