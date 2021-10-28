import unittest
from unittest.mock import patch
from werkzeug.datastructures import ImmutableMultiDict
from app.application import app
from parameterized import parameterized


class TestResourcesCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    @parameterized.expand([
        ('app.resources.get_student', '/students/1/', [1]),
        ('app.resources.get_course', '/courses/1/', [1]),
        ('app.resources.get_group', '/groups/1/', [1]),
        ('app.resources.get_all_students', '/students/', []),
        ('app.resources.get_all_courses', '/courses/', []),
        ('app.resources.get_all_groups', '/groups/', []),
    ])
    def test_get_methods(self, mocked_function_target, resource_path, expected_call_args):
        with patch(mocked_function_target) as mocked_function:
            mocked_function.return_value = 'sample data'
            answer = self.app.get(resource_path)
            self.assertTrue('sample data' in answer.data.decode('utf8'))
            mocked_function.assert_called_with(*expected_call_args)

    @parameterized.expand([
        ('app.resources.put_student', '/students/1/'),
        ('app.resources.put_course', '/courses/1/'),
        ('app.resources.put_group', '/groups/1/'),
    ])
    def test_put_methods(self, mocked_function_target, resource_path):
        with patch(mocked_function_target) as mocked_function:
            mocked_function.return_value = 'sample data'
            answer = self.app.put(resource_path, data={'test_key': 'test_value'})
            self.assertTrue('sample data' in answer.data.decode('utf8'))
            mocked_function.assert_called_with(1, ImmutableMultiDict([('test_key', 'test_value')]))

    @parameterized.expand([
        ('app.resources.delete_student', '/students/1/'),
        ('app.resources.delete_course', '/courses/1/'),
        ('app.resources.delete_group', '/groups/1/'),
    ])
    def test_delete_methods(self, mocked_function_target, resource_path):
        with patch(mocked_function_target) as mocked_function:
            mocked_function.return_value = 'sample data'
            answer = self.app.delete(resource_path)
            self.assertTrue('sample data' in answer.data.decode('utf8'))
            mocked_function.assert_called_with(1)

    @parameterized.expand([
        ('app.resources.post_student', '/students/'),
        ('app.resources.post_course', '/courses/'),
        ('app.resources.post_group', '/groups/'),
    ])
    def test_post_methods(self, mocked_function_target, resource_path):
        with patch(mocked_function_target) as mocked_function:
            mocked_function.return_value = 'sample data'
            answer = self.app.post(resource_path, data={'test_key': 'test_value'})
            self.assertTrue('sample data' in answer.data.decode('utf8'))
            mocked_function.assert_called_with(ImmutableMultiDict([('test_key', 'test_value')]))

    @parameterized.expand([
        ('put', 'app.resources.put_student', '/students/1/'),
        ('put', 'app.resources.put_course', '/courses/1/'),
        ('put', 'app.resources.put_group', '/groups/1/'),
        ('delete', 'app.resources.delete_student', '/students/1/'),
        ('delete', 'app.resources.delete_course', '/courses/1/'),
        ('delete', 'app.resources.delete_group', '/groups/1/'),
        ('post', 'app.resources.post_student', '/students/'),
        ('post', 'app.resources.post_course', '/courses/'),
        ('post', 'app.resources.post_group', '/groups/'),
    ])
    def test_exception_methods(self, api_method, mocked_function_target, resource_path):
        with patch(mocked_function_target) as mocked_function:
            mocked_function.side_effect = AssertionError('sample exception massage')
            answer = getattr(self.app, api_method)(resource_path)
            self.assertTrue('sample exception massage' in answer.data.decode('utf8'))


if __name__ == '__main__':
    unittest.main()