import unittest
import testing.postgresql
import psycopg2
from app.application import app, db
from app.models import StudentModel, GroupModel


class TestCase(unittest.TestCase):
    def setUp(self):
        self.postgresql = testing.postgresql.Postgresql(port=7654)
        # Get the url to connect to with psycopg2 or equivalent
        print(self.postgresql.url())

    def test_student_model(self):
        with self.testing.postgresql.Postgresql(port=7654) as psql:
            pass

    def tearDown(self):
        self.postgresql.stop()


if __name__ == '__main__':
    unittest.main()
