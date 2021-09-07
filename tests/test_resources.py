import unittest
import json
import testing.postgresql
from parameterized import parameterized
from app.config import Configuration

postgresql = testing.postgresql.Postgresql(port=7654)
Configuration.SQLALCHEMY_DATABASE_URI = postgresql.url()

from app.application import app, db
from app.models import students_courses_relation, StudentModel, GroupModel, CourseModel


class TestGetMethodCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.create_all()

    def setUp(self):
        print(StudentModel.query.all())

        self.app = app.test_client()


        db.session.query(students_courses_relation).delete()
        GroupModel.query.delete()
        CourseModel.query.delete()
        StudentModel.query.delete()
        db.session.execute("ALTER SEQUENCE students_id_seq RESTART WITH 1")
        db.session.execute("ALTER SEQUENCE groups_id_seq RESTART WITH 1")
        db.session.execute("ALTER SEQUENCE courses_id_seq RESTART WITH 1")
        db.session.commit()

    def create_test_student(self):
        student = StudentModel(1, 'test_first_name', 'test_last_name')
        db.session.add(student)
        db.session.commit()

    def create_test_group(self):
        group = GroupModel('aa-11')
        db.session.add(group)
        db.session.commit()

    def create_test_course(self):
        course = CourseModel('test_name', 'test_description')
        db.session.add(course)
        db.session.commit()

    def create_test_student_with_course(self):
        self.create_test_student()
        self.create_test_course()

        student = StudentModel.query.first()
        course = CourseModel.query.first()
        student.courses.append(course)


    @parameterized.expand([
        ('/students/1/',),
        ('/students/5/',),
        ('/courses/1/',),
        ('/courses/7/',),
        ('/groups/1/',),
        ('/groups/10/',),
    ])
    def test_without_data(self, route):
        answer = self.app.get(route)

        self.assertEqual(answer.data.decode("utf-8").strip(), '{}')

    def test_groups(self):
        self.create_test_group()

        answer = self.app.get('/groups/1/')
        data = json.loads(answer.data.decode("utf-8"))

        self.assertEqual(data['name'], 'aa-11')
        self.assertEqual(data['students_ids'], [])

    def test_groups_with_students(self):
        self.create_test_group()
        self.create_test_student()

        answer = self.app.get('/groups/1/')
        data = json.loads(answer.data.decode("utf-8"))

        self.assertEqual(data['students_ids'], [1])

    def test_students(self):
        self.create_test_group()
        self.create_test_student()

        answer = self.app.get('/students/1/')
        data = json.loads(answer.data.decode("utf-8"))

        self.assertEqual(data['first_name'], 'test_first_name')
        self.assertEqual(data['last_name'], 'test_last_name')
        self.assertEqual(data['courses_ids'], [])

    def test_students_with_courses(self):
        self.create_test_group()
        self.create_test_student_with_course()

        answer = self.app.get('/students/1/')
        data = json.loads(answer.data.decode("utf-8"))

        self.assertEqual(data['courses_ids'], [1])

    def test_courses(self):
        self.create_test_course()

        answer = self.app.get('/courses/1/')
        data = json.loads(answer.data.decode("utf-8"))

        self.assertEqual(data['name'], 'test_name')
        self.assertEqual(data['description'], 'test_description')
        self.assertEqual(data['students_ids'], [])

    def test_courses_with_students(self):
        self.create_test_group()
        self.create_test_student_with_course()

        answer = self.app.get('/courses/1/')
        data = json.loads(answer.data.decode("utf-8"))

        self.assertEqual(data['students_ids'], [1])


if __name__ == '__main__':
    unittest.main()