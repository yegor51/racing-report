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
    """add example item to `students` table."""
    for num in range(1, count + 1):
        student = StudentModel(1, f'first_name_{num}', f'last_name_{num}')
        db.session.add(student)
    db.session.commit()


def create_test_groups(count=1):
    """add example item to `groups` table."""
    for num in range(1, count + 1):
        group = GroupModel(f'aa-{str(num).zfill(2)}')
        db.session.add(group)
    db.session.commit()


def create_test_courses(count=1):
    """add example item to `courses` table."""
    for num in range(1, count+1):
        course = CourseModel(f'test_name_{num}', f'test_description_{num}')
        db.session.add(course)
    db.session.commit()


def create_test_student_with_course():
    """add example items to `students` and `courses` tables and create relation between them."""
    create_test_students(1)
    create_test_courses(1)

    student = StudentModel.query.first()
    course = CourseModel.query.first()
    student.courses.append(course)


class TestGetMethodCase(unittest.TestCase):

    def setUp(self):
        """clear all data from test database after previous test."""
        self.app = app.test_client()
        db.session.commit()
        db.drop_all()
        db.create_all()
        db.session.commit()

    @parameterized.expand([
        ('/students/1/',),
        ('/students/5/',),
        ('/courses/1/',),
        ('/courses/7/',),
        ('/groups/1/',),
        ('/groups/10/',),
    ])
    def test_without_data(self, route):
        """test GET methods. all resources should return '{}' if no data
         in database or such object not found"""
        answer = self.app.get(route)

        self.assertEqual(answer.data.decode("utf-8").strip(), '{}')

    def test_groups(self):
        """test GroupResource GET method data displaying.
        returned data should contain name of the group."""
        create_test_groups(1)

        answer = self.app.get('/groups/1/')
        data = json.loads(answer.data.decode("utf-8"))

        self.assertEqual(data['name'], 'aa-01')
        self.assertEqual(data['students_ids'], [])

    def test_groups_with_students(self):
        """test GroupResource GET method data displaying.
        returned data should contain list of student IDs of this group."""
        create_test_groups(1)
        create_test_students(1)

        answer = self.app.get('/groups/1/')
        data = json.loads(answer.data.decode("utf-8"))

        self.assertEqual(data['students_ids'], [1])

    def test_students(self):
        """test StudentResource GET method data displaying.
        returned data should contain first and last names of this student.
        """
        create_test_groups(1)
        create_test_students(1)

        answer = self.app.get('/students/1/')
        data = json.loads(answer.data.decode("utf-8"))

        self.assertEqual(data['first_name'], 'first_name_1')
        self.assertEqual(data['last_name'], 'last_name_1')
        self.assertEqual(data['courses_ids'], [])

    def test_students_with_courses(self):
        """test StudentResource GET method data displaying.
        returned data should contain list of course IDs of this student.
        """
        create_test_groups(1)
        create_test_student_with_course()

        answer = self.app.get('/students/1/')
        data = json.loads(answer.data.decode("utf-8"))

        self.assertEqual(data['courses_ids'], [1])

    def test_courses(self):
        """test CourseResource GET method data displaying.
        returned data should contain name and description of this course.
        """
        create_test_courses(1)

        answer = self.app.get('/courses/1/')
        data = json.loads(answer.data.decode("utf-8"))

        self.assertEqual(data['name'], 'test_name_1')
        self.assertEqual(data['description'], 'test_description_1')
        self.assertEqual(data['students_ids'], [])

    def test_courses_with_students(self):
        """test CourseResource GET method data displaying.
        returned data should contain list of student IDs, joined to this course.
        """
        create_test_groups(1)
        create_test_student_with_course()

        answer = self.app.get('/courses/1/')
        data = json.loads(answer.data.decode("utf-8"))

        self.assertEqual(data['students_ids'], [1])

    def test_students_list(self):
        create_test_groups(1)
        create_test_students(2)

        answer = self.app.get('/students/')
        data = json.loads(answer.data.decode("utf-8"))

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['first_name'], 'first_name_1')
        self.assertEqual(data[0]['last_name'], 'last_name_1')
        self.assertEqual(data[1]['id'], 2)
        self.assertEqual(data[1]['first_name'], 'first_name_2')
        self.assertEqual(data[1]['last_name'], 'last_name_2')

    def test_courses_list(self):
        create_test_courses(2)

        answer = self.app.get('/courses/')
        data = json.loads(answer.data.decode("utf-8"))

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['name'], 'test_name_1')
        self.assertEqual(data[0]['description'], 'test_description_1')
        self.assertEqual(data[1]['id'], 2)
        self.assertEqual(data[1]['name'], 'test_name_2')
        self.assertEqual(data[1]['description'], 'test_description_2')

    def test_groups_list(self):
        create_test_groups(2)

        answer = self.app.get('/groups/')
        data = json.loads(answer.data.decode("utf-8"))

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['name'], 'aa-01')
        self.assertEqual(data[1]['id'], 2)
        self.assertEqual(data[1]['name'], 'aa-02')


class TestPostMethodCase(unittest.TestCase):

    def setUp(self):
        """clear all data from test database after previous test."""
        self.app = app.test_client()
        db.session.commit()
        db.drop_all()
        db.create_all()
        db.session.commit()

    def test_student(self):
        create_test_groups()
        self.app.post('/students/', data={'first_name': 'test_first_name',
                      'last_name': 'test_last_name',
                      'group_id': 1})

        students = StudentModel.query.all()

        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].first_name, 'test_first_name')
        self.assertEqual(students[0].last_name, 'test_last_name')
        self.assertEqual(students[0].group_id, 1)

    def test_student_without_group(self):
        answer = self.app.post('/students/', data={'first_name': 'test_first_name',
                                                   'last_name': 'test_last_name',
                                                   'group_id': 1,
                                                   })

        self.assertIn('ERROR: incorrect data.', answer.data.decode("utf-8"))

        students = StudentModel.query.all()

        self.assertEqual(len(students), 0)

    def test_student_with_incomplete_data(self):
        create_test_groups()
        answer = self.app.post('/students/', data={'first_name': 'test_first_name',
                                                   'group_id': 1,
                                                   })

        self.assertIn('ERROR: all parameters (first_name, last_name, group_id) must be specified.',
                      answer.data.decode("utf-8"))

        students = StudentModel.query.all()

        self.assertEqual(len(students), 0)

    def test_course(self):
        self.app.post('/courses/', data={'name': 'test_name',
                                         'description': 'test_description'})

        courses = CourseModel.query.all()

        self.assertEqual(len(courses), 1)
        self.assertEqual(courses[0].name, 'test_name')
        self.assertEqual(courses[0].description, 'test_description')

    def test_course_with_incomplete_data(self):
        answer = self.app.post('/courses/', data={'name': 'test_name'})

        self.assertIn('ERROR: all parameters (name, description) must be specified.',
                      answer.data.decode("utf-8"))

        courses = CourseModel.query.all()

        self.assertEqual(len(courses), 0)

    def test_group(self):
        self.app.post('/groups/', data={'name': 'aa-11'})
        groups = GroupModel.query.all()

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].name, 'aa-11')

    def test_group_with_incomplete_data(self):
        answer = self.app.post('/groups/')

        self.assertIn('ERROR: parameter `name` must be specified.',
                      answer.data.decode("utf-8"))

        groups = GroupModel.query.all()

        self.assertEqual(len(groups), 0)

    def test_group_with_incorrect_name(self):
        answer = self.app.post('/groups/', data={'name': 'test_name'})

        self.assertIn('ERROR: wrong name format.', answer.data.decode("utf-8"))

        groups = GroupModel.query.all()

        self.assertEqual(len(groups), 0)


class TestPutMethodCase(unittest.TestCase):
    def setUp(self):
        """clear all data from test database after previous test."""
        self.app = app.test_client()
        db.session.commit()
        db.drop_all()
        db.create_all()
        db.session.commit()

    def test_student(self):
        create_test_groups()
        create_test_students(1)

        self.app.put('/students/1/', data={'first_name': 'changed_first_name'})

        student = StudentModel.query.first()

        self.assertEqual(student.first_name, 'changed_first_name')
        self.assertEqual(student.last_name, 'last_name_1')
        self.assertEqual(student.group_id, 1)

    def test_student_few_changes(self):
        create_test_groups(2)
        create_test_students(1)

        self.app.put('/students/1/', data={'first_name': 'changed_first_name',
                                           'last_name': 'changed_last_name',
                                           'group_id': 2})

        student = StudentModel.query.first()

        self.assertEqual(student.first_name, 'changed_first_name')
        self.assertEqual(student.last_name, 'changed_last_name')
        self.assertEqual(student.group_id, 2)

    def test_student_incorrect_group_id(self):
        create_test_groups()
        create_test_students(1)

        answer = self.app.put('/students/1/', data={'group_id': 2})

        self.assertIn('ERROR: incorrect data.', answer.data.decode("utf-8"))

        student = StudentModel.query.first()

        self.assertEqual(student.group_id, 1)

    def test_student_with_wrong_id(self):
        create_test_groups()
        create_test_students(1)

        answer = self.app.put('/students/100/', data={'group_id': 2})

        self.assertIn('ERROR: student with id 100 not exist.', answer.data.decode("utf-8"))

        student = StudentModel.query.first()

        self.assertEqual(student.group_id, 1)

    def test_group(self):
        create_test_groups(1)

        self.app.put('/groups/1/', data={'name': 'aa-99'})

        group = GroupModel.query.first()

        self.assertEqual(group.name, 'aa-99')

    def test_group_with_wrong_name_format(self):
        create_test_groups(1)

        answer = self.app.put('/groups/1/', data={'name': 'test_name'})

        self.assertIn('ERROR: wrong name format.', answer.data.decode("utf-8"))

        group = GroupModel.query.first()

        self.assertEqual(group.name, 'aa-01')

    def test_group_with_wrong_id(self):
        create_test_groups(1)

        answer = self.app.put('/groups/100/', data={'name': 'test_name'})

        self.assertIn('ERROR: group with id 100 not exist.', answer.data.decode("utf-8"))

        group = GroupModel.query.first()

        self.assertEqual(group.name, 'aa-01')

    def test_courses(self):
        create_test_courses(1)

        self.app.put('/courses/1/', data={'name': 'changed_name'})

        course = CourseModel.query.first()

        self.assertEqual(course.name, 'changed_name')
        self.assertEqual(course.description, 'test_description_1')

    def test_courses_with_few_changes(self):
        create_test_courses(1)

        self.app.put('/courses/1/', data={'name': 'changed_name', 'description': 'changed_description'})

        course = CourseModel.query.first()

        self.assertEqual(course.name, 'changed_name')
        self.assertEqual(course.description, 'changed_description')

    def test_courses_with_wrong_id(self):
        create_test_courses(1)

        answer = self.app.put('/courses/100/', data={'name': 'changed_name'})

        self.assertIn('ERROR: course with id None not exist.', answer.data.decode("utf-8"))

        course = CourseModel.query.first()

        self.assertEqual(course.name, 'test_name_1')


class TestDeleteMethodCase(unittest.TestCase):
    def setUp(self):
        """clear all data from test database after previous test."""
        db.session.commit()
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        db.session.commit()

    def test_student(self):
        create_test_groups()
        create_test_students(2)

        self.app.delete('/students/1/')

        students = StudentModel.query.all()

        self.assertEqual(len(students), 1)

        self.assertEqual(students[0].id, 2)

    def test_student_with_wrong_id(self):
        create_test_groups()
        create_test_students(1)

        answer = self.app.delete('/students/100/')

        self.assertIn('ERROR: student with id 100 not exist.', answer.data.decode("utf-8"))

        students = StudentModel.query.all()

        self.assertEqual(len(students), 1)

    def test_group(self):
        create_test_groups(2)

        self.app.delete('/groups/1/')

        groups = GroupModel.query.all()

        self.assertEqual(len(groups), 1)

        self.assertEqual(groups[0].id, 2)

    def test_group_with_wrong_id(self):
        create_test_groups(1)

        answer = self.app.delete('/groups/100/')

        self.assertIn('ERROR: group with id 100 not exist.', answer.data.decode("utf-8"))

        groups = GroupModel.query.all()

        self.assertEqual(len(groups), 1)

    def test_course(self):
        create_test_courses(2)

        self.app.delete('/courses/1/')

        courses = CourseModel.query.all()

        self.assertEqual(len(courses), 1)

        self.assertEqual(courses[0].id, 2)

    def test_course_with_wrong_id(self):
        create_test_courses(1)

        answer = self.app.delete('/courses/100/')

        self.assertIn('ERROR: course with id 100 not exist.', answer.data.decode("utf-8"))

        courses = CourseModel.query.all()

        self.assertEqual(len(courses), 1)

    def test_group_with_student(self):
        create_test_groups(1)
        create_test_students(2)

        answer = self.app.delete('/groups/1/')

        self.assertIn('ERROR: cannot delete the group with students. Student ids: 1, 2',
                      answer.data.decode("utf-8"))

        groups = GroupModel.query.all()

        self.assertEqual(len(groups), 1)

    def test_student_with_course(self):
        create_test_groups(1)
        create_test_student_with_course()

        self.app.delete('/students/1/')

        self.assertFalse(StudentModel.query.all())
        self.assertFalse(CourseModel.query.first().students)

    def test_course_with_students(self):
        create_test_groups(1)
        create_test_student_with_course()

        self.app.delete('/courses/1/')

        self.assertFalse(CourseModel.query.all())
        self.assertFalse(StudentModel.query.first().courses)


if __name__ == '__main__':
    unittest.main()