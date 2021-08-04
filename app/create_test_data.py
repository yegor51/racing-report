import random
import string
from .application import db
from .models import GroupModel, CourseModel, StudentModel, students_courses_relation


def clear_all_tables():
    StudentModel.query.delete()
    CourseModel.query.delete()
    GroupModel.query.delete()
    students_courses_relation.delete()


def get_random_group_name():
    name = ''
    for _ in range(2):
        name += random.choice(string.ascii_lowercase)

    name += '-'

    for _ in range(2):
        name += random.choice(string.digits)

    return name


def create_groups():
    for i in range(10):
        group = GroupModel(get_random_group_name())
        db.session.add(group)


def create_courses():
    courses = ['math', 'biology', 'art', 'geography', 'history',
               'english', 'chemistry', 'physics', 'Marketing', 'management']

    for course_name in courses:
        course = CourseModel(course_name, 'The course of {}.'.format(course_name))
        db.session.add(course)


def get_random_group_id():
    return random.choice(GroupModel.query.all()).id


def create_students():
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
    courses_list = CourseModel.query.all()

    for student in StudentModel.query.all():
        for courses in random.sample(courses_list, random.randint(1, 3)):
            student.courses.append(courses)


def create_test_data():
    clear_all_tables()
    create_groups()
    create_students()
    create_courses()
    create_students_courses_relation()
    db.session.commit()


if __name__ == '__main__':
    create_test_data()
