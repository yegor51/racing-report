import unittest
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


class TestDatabaseWorkingMethodsCase(unittest.TestCase):

    def setUp(self):
        """clear all data from test database after previous test."""
        db.session.commit()
        db.drop_all()
        db.create_all()
        db.session.commit()

    @parameterized.expand([
        (GroupModel,),
        (CourseModel,),
        (StudentModel,),
    ])
    def test_get_item(self, database_model):
        create_test_groups(2)
        create_test_students(2)
        create_test_courses(2)

        item = database_model.get_item(2)

        self.assertEqual(type(item), database_model)
        self.assertEqual(item.id, 2)

    @parameterized.expand([
        (GroupModel,),
        (CourseModel,),
        (StudentModel,),
    ])
    def test_get_item_with_false_id(self, database_model):

        item = database_model.get_item(5)

        self.assertEqual(item, None)

    def test_group_model_get_params_dict(self):
        create_test_groups(1)

        data = GroupModel.get_item(1).get_params_dict()

        self.assertEqual(data['name'], 'aa-01')
        self.assertEqual(data['students_ids'], [])

    def test_group_model_get_params_dict_with_students(self):
        create_test_groups(1)
        create_test_students(1)

        data = GroupModel.get_item(1).get_params_dict()

        self.assertEqual(data['students_ids'], [1])

    def test_student_model_get_params_dict(self):
        create_test_groups(1)
        create_test_students(1)

        data = StudentModel.get_item(1).get_params_dict()

        self.assertEqual(data['first_name'], 'first_name_1')
        self.assertEqual(data['last_name'], 'last_name_1')
        self.assertEqual(data['courses_ids'], [])

    def test_student_model_get_params_dict_with_courses(self):
        create_test_groups(1)
        create_test_student_with_course()

        data = StudentModel.get_item(1).get_params_dict()

        self.assertEqual(data['courses_ids'], [1])

    def test_course_model_get_params_dict(self):
        create_test_courses(1)

        data = CourseModel.get_item(1).get_params_dict()

        self.assertEqual(data['name'], 'test_name_1')
        self.assertEqual(data['description'], 'test_description_1')
        self.assertEqual(data['students_ids'], [])

    def test_course_model_with_students(self):
        create_test_groups(1)
        create_test_student_with_course()

        data = CourseModel.get_item(1).get_params_dict()

        self.assertEqual(data['students_ids'], [1])

    def test_student_model_get_all_items_params_dict(self):
        create_test_groups(2)
        create_test_students(2)

        data = StudentModel.get_all_items_params_dict()

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['first_name'], 'first_name_1')
        self.assertEqual(data[0]['last_name'], 'last_name_1')
        self.assertEqual(data[1]['id'], 2)
        self.assertEqual(data[1]['first_name'], 'first_name_2')
        self.assertEqual(data[1]['last_name'], 'last_name_2')

    def test_course_model_get_all_items_params_dict(self):
        """test get_all_courses function"""
        create_test_courses(2)

        data = CourseModel.get_all_items_params_dict()

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['name'], 'test_name_1')
        self.assertEqual(data[0]['description'], 'test_description_1')
        self.assertEqual(data[1]['id'], 2)
        self.assertEqual(data[1]['name'], 'test_name_2')
        self.assertEqual(data[1]['description'], 'test_description_2')

    def test_group_model_get_all_items_params_dict(self):
        """test get_all_group function"""
        create_test_groups(2)

        data = GroupModel.get_all_items_params_dict()

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['name'], 'aa-01')
        self.assertEqual(data[1]['id'], 2)
        self.assertEqual(data[1]['name'], 'aa-02')

    @parameterized.expand([
        (StudentModel, {'first_name': 'test_first_name', 'last_name': 'test_last_name', 'group_id': 1}),
        (CourseModel, {'name': 'test_name', 'description': 'test_description'}),
        (GroupModel, {'name': 'aa-11'}),
    ])
    def test_models_post_item(self, database_model, params):
        if database_model == StudentModel:
            create_test_groups()

        database_model.post_item(**params)

        items = database_model.query.all()

        self.assertEqual(len(items), 1)
        for (param_name, param) in params.items():
            self.assertEqual(getattr(items[0], param_name), param)

    @parameterized.expand([
        (StudentModel, {'first_name': 'test_first_name', 'last_name': 'test_last_name', 'group_id': 10}),
        (StudentModel, {'first_name': 'test_first_name', 'group_id': 1}),
        (CourseModel, {'name': 'test_name'}),
        (GroupModel, {'name': 'test_name'}),
        (GroupModel, {}),
        ])
    def test_models_post_item_incorrect_data(self, database_model, params):
        if database_model == StudentModel:
            create_test_groups()

        with self.assertRaises(AssertionError):
            database_model.post_item(**params)

        items = database_model.query.all()

        self.assertEqual(len(items), 0)

    @parameterized.expand([
        (StudentModel, {'first_name': 'test_first_name'}),
        (CourseModel, {'name': 'test_name'}),
        (GroupModel, {'name': 'aa-11'}),
        (StudentModel, {'first_name': 'test_first_name', 'last_name': 'test_last_name', 'group_id': 1}),
        (CourseModel, {'name': 'test_name', 'description': 'test_description'}),
        ])
    def test_models_put_params(self, database_model, params):
        create_test_groups(1)
        create_test_students(1)
        create_test_courses(1)

        database_model.get_item(1).put_params(**params)

        item = database_model.query.first()

        for (param_name, param) in params.items():
            self.assertEqual(getattr(item, param_name), param)

    @parameterized.expand([
        (GroupModel, {'name': 'test_name'}),
        (StudentModel, {'group_id': 'abc'}),
        ])
    def test_models_put_params_incorrect_data(self, database_model, params):
        create_test_groups(1)
        create_test_students(1)
        create_test_courses(1)

        with self.assertRaises(AssertionError):
            database_model.get_item(1).put_params(**params)

        item = database_model.query.first()

        for (param_name, param) in params.items():
            self.assertNotEqual(getattr(item, param_name), param)

    @parameterized.expand([
        (GroupModel,),
        (StudentModel,),
        (CourseModel,),
    ])
    def test_models_delete_item(self, database_model):
        create_test_groups(2)
        create_test_students(2)
        create_test_courses(2)

        database_model.delete_item(2)

        items = database_model.query.all()

        self.assertEqual(len(items), 1)

        self.assertEqual(items[0].id, 1)

    def test_delete_group_with_student(self):
        create_test_groups(1)
        create_test_students(2)

        with self.assertRaises(AssertionError):
            GroupModel.delete_item(1)

        groups = GroupModel.query.all()

        self.assertEqual(len(groups), 1)

    def test_delete_student_with_course(self):
        create_test_groups(1)
        create_test_student_with_course()

        StudentModel.delete_item(1)

        self.assertFalse(StudentModel.query.all())
        self.assertFalse(CourseModel.query.first().students)

    def test_delete_course_with_students(self):
        create_test_groups(1)
        create_test_student_with_course()

        CourseModel.delete_item(1)

        self.assertFalse(CourseModel.query.all())
        self.assertFalse(StudentModel.query.first().courses)


if __name__ == '__main__':
    unittest.main()