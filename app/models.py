"""
Contains SQLAlchemy models of tables
automatically creates all tables in the database, if they are not, and test data,
if any data not exist.

models:
    GroupModel
        fields:
            id (int, primary_key)
            name (str)

    CourseModel
        fields:
            id (int, primary_key)
            name (str)
            description (str)

    StudentModel
        fields:
            id (int, primary_key)
            first_name (str)
            last_name (str)
            group_id (int)

tables:
    students_courses_relation
        special table, that presents MANY-TO-MANY relation between StudentModel and
        CourseModel.
        columns:
            course_id (int, primary_key)
            student_id (int, primary_key)
"""
import re

from .application import app, db
from sqlalchemy.exc import IntegrityError, DataError


def is_group_name_fits(name):
    return re.search("[a-z][a-z]-[0-9][0-9]", name)


students_courses_relation = db.Table('students_courses_relation',
                        db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True),
                        db.Column('student_id', db.Integer, db.ForeignKey('students.id'), primary_key=True)
                        )


class DatabaseFunctionsMixin(object):

    @classmethod
    def get_item(cls, item_id):
        return db.session.get(cls, item_id)

    @classmethod
    def delete_item(cls, item_id):
        item = cls.query.filter_by(id=item_id).first()
        if not item:
            return f'item {item_id} was not found in {cls.__tablename__} table.'
        db.session.delete(item)
        db.session.commit()

        return f'deleted item {item_id}.'

    @classmethod
    def get_all_items_params_dict(cls):
        items = cls.query.all()
        return [item.get_params_dict() for item in items]


    @classmethod
    def post_item(cls, **params):
        columns_name_list = cls.__table__.columns.keys()
        columns_name_list.remove('id')
        for column_name in columns_name_list:
            assert column_name in params, '`{}` parameter missed'.format(column_name)

        new_item = cls(**{column_name: params[column_name] for column_name in columns_name_list})

        try:
            db.session.add(new_item)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise AssertionError('incorrect data.')

    def put_params(self, **params):
        for column_name in self.__table__.columns.keys():
            if column_name in params:
                setattr(self, column_name, params[column_name])

        try:
            db.session.commit()
        except (IntegrityError, DataError):
            db.session.rollback()
            raise AssertionError('Incorrect data.')

    def get_params_dict(self):
        return {column_name: getattr(self, column_name)
                for column_name in self.__table__.columns.keys()}


class StudentModel(db.Model, DatabaseFunctionsMixin):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    courses = db.relationship('CourseModel', secondary=students_courses_relation, lazy='subquery',
                              backref=db.backref('students', lazy=True))

    def __init__(self, group_id, first_name, last_name):
        self.group_id = group_id
        self.first_name = first_name
        self.last_name = last_name

    def get_params_dict(self):
        params_dict = super(StudentModel, self).get_params_dict()

        courses = db.session.query(students_courses_relation).filter_by(student_id=self.id)
        params_dict['courses_ids'] = [course.course_id for course in courses]
        return params_dict


class GroupModel(db.Model, DatabaseFunctionsMixin):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        self.name = name

    def get_params_dict(self):
        params_dict = super(GroupModel, self).get_params_dict()

        students = db.session.query(StudentModel).filter_by(group_id=self.id)
        params_dict['students_ids'] = [student.id for student in students]
        return params_dict

    def put_params(self, **params):
        if 'name' in params:
            assert is_group_name_fits(params['name']), 'wrong group name format.'

        return super(GroupModel, self).put_params(**params)

    @classmethod
    def delete_item(cls, item_id):
        students = db.session.query(StudentModel).filter_by(group_id=item_id).all()

        assert not students, \
            'cannot delete the group with students. Student ids: {}' \
                .format(', '.join([str(student.id) for student in students]))

        return super(GroupModel, cls).delete_item(item_id)

    @classmethod
    def post_item(cls, **params):
        assert 'name' in params and is_group_name_fits(params['name']), 'wrong group name format.'

        super(GroupModel, cls).post_item(**params)


class CourseModel(db.Model, DatabaseFunctionsMixin):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def get_params_dict(self):
        params_dict = super(CourseModel, self).get_params_dict()

        students = db.session.query(students_courses_relation).filter_by(course_id=self.id)
        params_dict['students_ids'] = [student.student_id for student in students]
        return params_dict


if not db.engine.table_names() or GroupModel.query.count() == 0 or CourseModel.query.count() == 0:
    from app.create_test_data import create_test_data
    db.create_all()
    create_test_data()
