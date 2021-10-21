import re
from .application import api, db
from .models import StudentModel, CourseModel, GroupModel, students_courses_relation
from sqlalchemy.exc import IntegrityError


def get_student(student_id):
    """return data about student by student id from the `students` table in json format."""
    student = StudentModel.query.filter_by(id=student_id).first()

    if not student:
        db.session.rollback()
        raise AssertionError('student with id {} not exist'.format(student_id))

    courses = db.session.query(students_courses_relation).filter_by(student_id=student_id)
    return {'first_name': student.first_name,
            'last_name': student.last_name,
            'group_id': student.group_id,
            'courses_ids': [course.course_id for course in courses],
            }


def put_student(student_id, data):
    student = StudentModel.query.filter_by(id=student_id).first()

    if not student:
        db.session.rollback()
        raise AssertionError('student with id {} not exist'.format(student_id))

    if 'first_name' in data:
        student.first_name = data['first_name']

    if 'last_name' in data:
        student.last_name = data['last_name']

    if 'group_id' in data:
        student.group_id = data['group_id']

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AssertionError('Incorrect data.')

    return {'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'group_id': student.group_id,
            }


def delete_student(student_id):
    student = StudentModel.query.filter_by(id=student_id).first()

    assert student, 'student with id {} not exist.'.format(student_id)

    db.session.delete(student)
    db.session.commit()

    return 'deleted student {}.'.format(student_id)


def get_course(course_id):
    """return data about course by course id from the `courses` table in json format."""
    course = CourseModel.query.filter_by(id=course_id).first()

    if not course:
        db.session.rollback()
        raise AssertionError('course with id {} not exist'.format(course_id))

    students = db.session.query(students_courses_relation).filter_by(course_id=course_id)
    return {'name': course.name,
            'description': course.description,
            'students_ids': [student.student_id for student in students],
            }


def put_course(course_id, data):
    course = CourseModel.query.filter_by(id=course_id).first()

    assert course, 'course with id {} not exist.'.format(course)

    if 'name' in data:
        course.name = data['name']

    if 'description' in data:
        course.description = data['description']

    db.session.commit()

    return {
        'id': course.id,
        'name': course.name,
        'description': course.description,
    }


def delete_course(course_id):
    course = CourseModel.query.filter_by(id=course_id).first()

    assert course, 'course with id {} not exist.'.format(course_id)

    db.session.delete(course)
    db.session.commit()

    return 'deleted course {}.'.format(course_id)


def get_group(group_id):
    """return data about group by group id from the 'groups' table in json format."""
    group = GroupModel.query.filter_by(id=group_id).first()

    if not group:
        db.session.rollback()
        raise AssertionError('group with id {} not exist'.format(group))

    students = db.session.query(StudentModel).filter_by(group_id=group_id)
    return {'name': group.name,
            'students_ids': [student.id for student in students],
            }


def put_group(group_id, data):
    group = GroupModel.query.filter_by(id=group_id).first()
    assert group, 'group with id {} not exist.'.format(group_id)

    if 'name' in data:
        group_name = data['name']

        assert re.search("[a-z][a-z]-[0-9][0-9]", group_name), 'wrong name format.'

        group.name = group_name

    db.session.commit()

    return {'id': group.id, 'name': group.name}


def delete_group(group_id):
    group = GroupModel.query.filter_by(id=group_id).first()

    assert group, 'group with id {} not exist.'.format(group_id)

    students = db.session.query(StudentModel).filter_by(group_id=group_id).all()

    assert not students, \
        'cannot delete the group with students. Student ids: {}'\
            .format(', '.join([str(student.id) for student in students]))

    db.session.delete(group)
    db.session.commit()

    return 'deleted group {}'.format(group_id)


def get_all_students():
    students = StudentModel.query.all()
    students_list = [
        {
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'group_id': student.group_id,
         }
        for student in students]

    return students_list


def post_student(data):
    student_first_name = data.get('first_name')
    student_last_name = data.get('last_name')
    student_group_id = data.get('group_id')

    assert None not in (student_first_name, student_last_name, student_group_id),\
        "all parameters (first_name, last_name, group_id) must be specified."

    student = StudentModel(student_group_id, student_first_name, student_last_name)

    try:
        db.session.add(student)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AssertionError('incorrect data.')

    return {
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'group_id': student.group_id,
         }


def get_all_courses():
    courses = CourseModel.query.all()
    courses_list = [
        {
            'id': course.id,
            'name': course.name,
            'description': course.description,
        }
        for course in courses]

    return courses_list


def post_course(data):
    course_name = data.get('name')
    course_description = data.get('description')

    assert None not in (course_name, course_description), \
        "all parameters (name, description) must be specified."

    course = CourseModel(course_name, course_description)

    try:
        db.session.add(course)
        db.session.commit()
    except IntegrityError:
        raise AssertionError('incorrect data.')

    return {
            'id': course.id,
            'first_name': course.name,
            'last_name': course.description,
         }


def get_all_groups():
    groups = GroupModel.query.all()
    groups_list = [
        {
            'id': group.id,
            'name': group.name,
        }
        for group in groups]

    return groups_list


def post_group(data):
    group_name = data.get('name')

    assert group_name, "parameter `name` must be specified."

    assert re.search("[a-z][a-z]-[0-9][0-9]", group_name), 'wrong name format.'

    group = GroupModel(group_name)

    try:
        db.session.add(group)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AssertionError('incorrect data.')