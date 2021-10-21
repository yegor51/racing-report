import unittest
import testing.postgresql
from parameterized import parameterized
from app.config import Configuration

postgresql = testing.postgresql.Postgresql(port=7654)
Configuration.SQLALCHEMY_DATABASE_URI = postgresql.url()

from app.application import app
from app.database_functions import *
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


class TestGetMethodsCase(unittest.TestCase):

    def setUp(self):
        """clear all data from test database after previous test."""
        db.session.commit()
        db.drop_all()
        db.create_all()
        db.session.commit()

    @parameterized.expand([
        (get_group,),
        (get_student,),
        (get_course,),
    ])
    def test_function_with_wrong_id(self, function):
        with self.assertRaises(AssertionError):
            function(5)

    def test_groups(self):
        create_test_groups(1)

        data = get_group(1)

        self.assertEqual(data['name'], 'aa-01')
        self.assertEqual(data['students_ids'], [])

    def test_groups_with_students(self):
        create_test_groups(1)
        create_test_students(1)

        data = get_group(1)

        self.assertEqual(data['students_ids'], [1])

    def test_students(self):
        create_test_groups(1)
        create_test_students(1)

        data = get_student(1)

        self.assertEqual(data['first_name'], 'first_name_1')
        self.assertEqual(data['last_name'], 'last_name_1')
        self.assertEqual(data['courses_ids'], [])

    def test_students_with_courses(self):
        create_test_groups(1)
        create_test_student_with_course()

        data = get_student(1)

        self.assertEqual(data['courses_ids'], [1])

    def test_courses(self):
        """test CourseResource GET method data displaying.
        returned data should contain name and description of this course.
        """
        create_test_courses(1)

        data = get_course(1)

        self.assertEqual(data['name'], 'test_name_1')
        self.assertEqual(data['description'], 'test_description_1')
        self.assertEqual(data['students_ids'], [])

    def test_courses_with_students(self):
        """test CourseResource GET method data displaying.
        returned data should contain list of student IDs, joined to this course.
        """
        create_test_groups(1)
        create_test_student_with_course()

        data = get_course(1)

        self.assertEqual(data['students_ids'], [1])

    def test_students_list(self):
        create_test_groups(1)
        create_test_students(2)

        data = get_all_students()

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['first_name'], 'first_name_1')
        self.assertEqual(data[0]['last_name'], 'last_name_1')
        self.assertEqual(data[1]['id'], 2)
        self.assertEqual(data[1]['first_name'], 'first_name_2')
        self.assertEqual(data[1]['last_name'], 'last_name_2')

    def test_courses_list(self):
        create_test_courses(2)

        data = get_all_courses()

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['name'], 'test_name_1')
        self.assertEqual(data[0]['description'], 'test_description_1')
        self.assertEqual(data[1]['id'], 2)
        self.assertEqual(data[1]['name'], 'test_name_2')
        self.assertEqual(data[1]['description'], 'test_description_2')

    def test_groups_list(self):
        create_test_groups(2)

        data = get_all_groups()

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['name'], 'aa-01')
        self.assertEqual(data[1]['id'], 2)
        self.assertEqual(data[1]['name'], 'aa-02')


class TestPostMethodsCase(unittest.TestCase):

    def setUp(self):
        """clear all data from test database after previous test."""
        db.session.commit()
        db.drop_all()
        db.create_all()
        db.session.commit()

    def test_student(self):
        create_test_groups()
        post_student(data={'first_name': 'test_first_name',
                           'last_name': 'test_last_name',
                           'group_id': 1})

        students = StudentModel.query.all()

        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].first_name, 'test_first_name')
        self.assertEqual(students[0].last_name, 'test_last_name')
        self.assertEqual(students[0].group_id, 1)

    def test_student_without_group(self):
        with self.assertRaises(AssertionError):
            post_student(data={'first_name': 'test_first_name',
                               'last_name': 'test_last_name',
                               'group_id': 1,
                               })

        students = StudentModel.query.all()

        self.assertEqual(len(students), 0)

    def test_student_with_incomplete_data(self):
        create_test_groups()

        with self.assertRaises(AssertionError):
            post_student(data={'first_name': 'test_first_name',
                               'group_id': 1,
                               })

        students = StudentModel.query.all()

        self.assertEqual(len(students), 0)

    def test_course(self):
        post_course(data={'name': 'test_name',
                          'description': 'test_description'})

        courses = CourseModel.query.all()

        self.assertEqual(len(courses), 1)
        self.assertEqual(courses[0].name, 'test_name')
        self.assertEqual(courses[0].description, 'test_description')

    def test_course_with_incomplete_data(self):
        with self.assertRaises(AssertionError):
            post_course(data={'name': 'test_name'})

        courses = CourseModel.query.all()

        self.assertEqual(len(courses), 0)

    def test_group(self):
        post_group(data={'name': 'aa-11'})
        groups = GroupModel.query.all()

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].name, 'aa-11')

    def test_group_with_incomplete_data(self):
        with self.assertRaises(AssertionError):
            post_group({})

        groups = GroupModel.query.all()

        self.assertEqual(len(groups), 0)

    def test_group_with_incorrect_name(self):
        with self.assertRaises(AssertionError):
            post_group(data={'name': 'test_name'})

        groups = GroupModel.query.all()

        self.assertEqual(len(groups), 0)


class TestPutMethodCase(unittest.TestCase):
    def setUp(self):
        """clear all data from test database after previous test."""
        db.session.commit()
        db.drop_all()
        db.create_all()
        db.session.commit()

    def test_student(self):
        create_test_groups()
        create_test_students(1)

        put_student(1, data={'first_name': 'changed_first_name'})

        student = StudentModel.query.first()

        self.assertEqual(student.first_name, 'changed_first_name')
        self.assertEqual(student.last_name, 'last_name_1')
        self.assertEqual(student.group_id, 1)

    def test_student_few_changes(self):
        create_test_groups(2)
        create_test_students(1)

        put_student(1, data={'first_name': 'changed_first_name',
                             'last_name': 'changed_last_name',
                             'group_id': 2})

        student = StudentModel.query.first()

        self.assertEqual(student.first_name, 'changed_first_name')
        self.assertEqual(student.last_name, 'changed_last_name')
        self.assertEqual(student.group_id, 2)

    def test_student_with_wrong_id(self):
        create_test_groups(1)
        create_test_students(1)

        with self.assertRaises(AssertionError):
            put_student(100, data={'group_id': 2})

        student = StudentModel.query.first()

        self.assertEqual(student.group_id, 1)

    def test_group(self):
        create_test_groups(1)

        put_group(1, data={'name': 'aa-99'})

        group = GroupModel.query.first()

        self.assertEqual(group.name, 'aa-99')

    def test_group_with_wrong_name_format(self):
        create_test_groups(1)

        with self.assertRaises(AssertionError):
            put_group(1, data={'name': 'test_name'})

        group = GroupModel.query.first()

        self.assertEqual(group.name, 'aa-01')

    def test_group_with_wrong_id(self):
        create_test_groups(1)

        with self.assertRaises(AssertionError):
            put_group(100, data={'name': 'test_name'})

        group = GroupModel.query.first()

        self.assertEqual(group.name, 'aa-01')

    def test_courses(self):
        create_test_courses(1)

        put_course(1, data={'name': 'changed_name'})

        course = CourseModel.query.first()

        self.assertEqual(course.name, 'changed_name')
        self.assertEqual(course.description, 'test_description_1')

    def test_courses_with_few_changes(self):
        create_test_courses(1)

        put_course(1, data={'name': 'changed_name', 'description': 'changed_description'})

        course = CourseModel.query.first()

        self.assertEqual(course.name, 'changed_name')
        self.assertEqual(course.description, 'changed_description')

    def test_courses_with_wrong_id(self):
        create_test_courses(1)

        with self.assertRaises(AssertionError):
            put_course(100, data={'name': 'changed_name'})

        course = CourseModel.query.first()

        self.assertEqual(course.name, 'test_name_1')


class TestDeleteMethodCase(unittest.TestCase):
    def setUp(self):
        """clear all data from test database after previous test."""
        db.session.commit()
        db.drop_all()
        db.create_all()
        db.session.commit()

    def test_student(self):
        create_test_groups()
        create_test_students(2)

        delete_student(1)

        students = StudentModel.query.all()

        self.assertEqual(len(students), 1)

        self.assertEqual(students[0].id, 2)

    def test_student_with_wrong_id(self):
        create_test_groups()
        create_test_students(1)

        with self.assertRaises(AssertionError):
            delete_student(100)

        students = StudentModel.query.all()

        self.assertEqual(len(students), 1)

    def test_group(self):
        create_test_groups(2)

        delete_group(1)

        groups = GroupModel.query.all()

        self.assertEqual(len(groups), 1)

        self.assertEqual(groups[0].id, 2)

    def test_group_with_wrong_id(self):
        create_test_groups(1)

        with self.assertRaises(AssertionError):
            delete_group(100)

        groups = GroupModel.query.all()

        self.assertEqual(len(groups), 1)

    def test_course(self):
        create_test_courses(2)

        delete_course(1)

        courses = CourseModel.query.all()

        self.assertEqual(len(courses), 1)

        self.assertEqual(courses[0].id, 2)

    def test_course_with_wrong_id(self):
        create_test_courses(1)

        with self.assertRaises(AssertionError):
            delete_course(100)

        courses = CourseModel.query.all()

        self.assertEqual(len(courses), 1)

    def test_group_with_student(self):
        create_test_groups(1)
        create_test_students(2)

        with self.assertRaises(AssertionError):
            delete_group(1)

        groups = GroupModel.query.all()

        self.assertEqual(len(groups), 1)

    def test_student_with_course(self):
        create_test_groups(1)
        create_test_student_with_course()

        delete_student(1)

        self.assertFalse(StudentModel.query.all())
        self.assertFalse(CourseModel.query.first().students)

    def test_course_with_students(self):
        create_test_groups(1)
        create_test_student_with_course()

        delete_course(1)

        self.assertFalse(CourseModel.query.all())
        self.assertFalse(StudentModel.query.first().courses)


if __name__ == '__main__':
    unittest.main()