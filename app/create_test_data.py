"""consist functions to generate test data (item 2 of Task 10)."""
import random
import string
from .application import db
from .models import GroupModel, CourseModel, StudentModel, students_courses_relation


def clear_all_tables():
    """delete all from the tables in the database."""
    StudentModel.query.delete()
    CourseModel.query.delete()
    GroupModel.query.delete()
    students_courses_relation.delete()


def get_random_group_name():
    """return string, composed from 2 random characters, hyphen, 2 random numbers."""
    name = ''
    for _ in range(2):
        name += random.choice(string.ascii_lowercase)

    name += '-'

    for _ in range(2):
        name += random.choice(string.digits)

    return name


def get_random_group_id():
    """return id of random group from `GroupModel` table."""
    return random.choice(GroupModel.query.all()).id


def create_groups():
    """fill `GroupModel` table with example data, 10 randomly named group objects."""
    for i in range(10):
        group = GroupModel(get_random_group_name())
        db.session.add(group)


def create_courses():
    """fill `CourseModel` table with example data, 10 courses with trivial descriptions."""
    courses = ['math', 'biology', 'art', 'geography', 'history',
               'english', 'chemistry', 'physics', 'Marketing', 'management']

    for course_name in courses:
        course = CourseModel(course_name, 'The course of {}.'.format(course_name))
        db.session.add(course)


def create_students():
    """fill `StudentModel` table with example data, 200 students with randomly combined
    first names\last names."""
    first_names = ['Liam', 'Noah', 'Oliver', 'Elijah', 'William',
                   'James', 'Benjamin', 'Lucas', 'Henry', 'Alexander',
                   'Olivia', 'Emma', 'Ava', 'Charlotte', 'Sophia',
                   'Amelia', 'Isabella', 'Mia', 'Evelyn', 'Harper']

    second_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones',
                    'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                    'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
                    'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']

    for _ in range(200):
        student = StudentModel(get_random_group_id(), random.choice(first_names), random.choice(second_names))
        db.session.add(student)


def create_students_courses_relation():
    """randomly assign from 1 to 3 courses for each student."""
    courses_list = CourseModel.query.all()

    for student in StudentModel.query.all():
        for courses in random.sample(courses_list, random.randint(1, 3)):
            student.courses.append(courses)


def create_test_data():
    """fill all tables in the database by example data."""
    clear_all_tables()
    create_groups()
    create_students()
    create_courses()
    create_students_courses_relation()
    db.session.commit()


if __name__ == '__main__':
    create_test_data()
