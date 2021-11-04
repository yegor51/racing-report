import unittest
import json
import testing.postgresql
from parameterized import parameterized
from app.config import Configuration

postgresql = testing.postgresql.Postgresql(port=7654)
Configuration.SQLALCHEMY_DATABASE_URI = postgresql.url()

from app.application import app, db
from app.models import StudentModel, GroupModel, CourseModel


def create_test_students(count=1):
    for num in range(1, count + 1):
        student = StudentModel(1, f'first_name_{num}', f'last_name_{num}')
        db.session.add(student)
    db.session.commit()


def create_test_groups(count=1):
    for num in range(1, count + 1):
        group = GroupModel(f'aa-{str(num).zfill(2)}')
        db.session.add(group)
    db.session.commit()


def create_test_courses(count=1):
    for num in range(1, count+1):
        course = CourseModel(f'test_name_{num}', f'test_description_{num}')
        db.session.add(course)
    db.session.commit()


def create_test_student_with_course():
    create_test_students(1)
    create_test_courses(1)

    student = StudentModel.query.first()
    course = CourseModel.query.first()
    student.courses.append(course)