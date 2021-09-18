"""create api resources using flask_restful module. Used json format for returned data.
resources:
    StudentResource:
        get method:
            return data about student by student id from the `students` table in json
            format.
            json keys:
                'first_name' - str, first name of student
                'last_name' - str, last name of student
                'group_id' - int, id of student group
                'courses_ids' - list of course IDs of this student

    CourseResource:
        get method:
             return data about course by course id from the `courses` table in json
             format.
             json keys:
                'name' - str, name of the course
                'description' - str, description of the course
                'students_ids' - list of student IDs, joined to the course

    GroupResource:
        get method:
            return data about group by group id from the 'groups' table in json format.
            json keys:
                'name' - str, name of the group
                'students_ids' - list of IDs of all students in this group"""
import re
from sqlalchemy.exc import IntegrityError
from flask import jsonify, request
from .application import api, db
from .models import StudentModel, CourseModel, GroupModel, students_courses_relation
from flask_restful import Resource


class StudentResource(Resource):
    def get(self, student_id):
        """return data about student by student id from the `students` table in json format."""
        student = StudentModel.query.filter_by(id=student_id).first()

        if not student:
            return {}

        courses = db.session.query(students_courses_relation).filter_by(student_id=student_id)
        return jsonify({'first_name': student.first_name,
                        'last_name': student.last_name,
                        'group_id': student.group_id,
                        'courses_ids': [course.course_id for course in courses],
                        })

    def put(self, student_id):
        student = StudentModel.query.filter_by(id=student_id).first()

        if not student:
            return 'ERROR: student with if {} not exist.'.format(student_id)

        if 'first_name' in request.form:
            student.first_name = request.form['first_name']

        if 'last_name' in request.form:
            student.last_name = request.form['last_name']

        if 'group_id' in request.form:
            student.group_id = request.form['group_id']

        db.session.commit()

        return {'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'group_id': student.group_id,
                }

    def delete(self, student_id):
        student = StudentModel.query.filter_by(id=student_id).first()

        if not student:
            return 'ERROR: student with if {} not exist.'.format(student_id)

        db.session.delete(student)
        db.session.commit()

        return 'deleted student {}.'.format(student_id)


class CourseResource(Resource):
    def get(self, course_id):
        """return data about course by course id from the `courses` table in json format."""
        course = CourseModel.query.filter_by(id=course_id).first()

        if not course:
            return {}

        students = db.session.query(students_courses_relation).filter_by(course_id=course_id)
        return jsonify({'name': course.name,
                        'description': course.description,
                        'students_ids': [student.student_id for student in students],
                        })

    def put(self, course_id):
        course = CourseModel.query.filter_by(id=course_id).first()

        if not course:
            return 'ERROR: course with if {} not exist.'.format(course)

        if 'name' in request.form:
            course.name = request.form['name']

        if 'description' in request.form:
            course.description = request.form['description']

        db.session.commit()

        return {
            'id': course.id,
            'name': course.name,
            'description': course.description,
        }

    def delete(self, course_id):
        course = CourseModel.query.filter_by(id=course_id).first()

        if not course:
            return 'ERROR: course with if {} not exist.'.format(course)

        db.session.delete(course)
        db.session.commit()

        return 'deleted course {}.'.format(course_id)


class GroupResource(Resource):
    def get(self, group_id):
        """return data about group by group id from the 'groups' table in json format."""
        group = GroupModel.query.filter_by(id=group_id).first()

        if not group:
            return {}

        students = db.session.query(StudentModel).filter_by(group_id=group_id)
        return jsonify({'name': group.name,
                        'students_ids': [student.id for student in students],
                        })

    def put(self, group_id):
        group = GroupModel.query.filter_by(id=group_id).first()
        if not group:
            return 'ERROR: group with if {} not exist.'.format(group_id)

        if 'name' in request.form:
            group_name = request.form['name']

            if not re.search("[a-z][a-z]-[0-9][0-9]", group_name):
                return 'ERROR: wrong name format.'

            group.name = group_name

        db.session.commit()

        return{'id': group.id, 'name': group.name}

    def delete(self, group_id):
        group = GroupModel.query.filter_by(id=group_id).first()
        if not group:
            return 'ERROR: group with if {} not exist.'.format(group_id)

        try:
            db.session.delete(group)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            students = db.session.query(StudentModel).filter_by(group_id=group_id)
            students_ids = [str(student.id) for student in students]
            return 'ERROR: cannot delete the group with students. Student ids: {}'.format(', '.join(students_ids))

        return 'deleted group {}'.format(group_id)


class StudentListResource(Resource):
    def get(self):
        students = StudentModel.query.all()
        students_list = [
            {
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'group_id': student.group_id,
             }
            for student in students]

        return jsonify(students_list)

    def post(self):
        student_first_name = request.form.get('first_name')
        student_last_name = request.form.get('last_name')
        student_group_id = request.form.get('group_id')

        if None in (student_first_name, student_last_name, student_group_id):
            return "ERROR: all parameters (first_name, last_name, group_id) must be specified."

        student = StudentModel(student_group_id, student_first_name, student_last_name)

        try:
            db.session.add(student)
            db.session.commit()
        except IntegrityError:
            return 'ERROR: incorrect data.'

        return {
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'group_id': student.group_id,
             }


class CourseListResource(Resource):
    def get(self):
        courses = CourseModel.query.all()
        courses_list = [
            {
                'id': course.id,
                'name': course.name,
                'description': course.description,
            }
            for course in courses]

        return jsonify(courses_list)

    def post(self):
        course_name = request.form.get('name')
        course_description = request.form.get('description')

        if None in (course_name, course_description):
            return "ERROR: all parameters (name, description) must be specified."

        course = CourseModel(course_name, course_description)

        try:
            db.session.add(course)
            db.session.commit()
        except IntegrityError:
            return 'ERROR: incorrect data.'

        return {
                'id': course.id,
                'first_name': course.name,
                'last_name': course.description,
             }


class GroupListResource(Resource):
    def get(self):
        groups = GroupModel.query.all()
        groups_list = [
            {
                'id': group.id,
                'name': group.name,
            }
            for group in groups]

        return jsonify(groups_list)

    def post(self):
        group_name = request.form.get('name')

        if not group_name:
            return "ERROR: parameter `name` must be specified."

        if not re.search("[a-z][a-z]-[0-9][0-9]", group_name):
            return 'ERROR: wrong name format.'

        group = GroupModel(group_name)

        try:
            db.session.add(group)
            db.session.commit()
        except IntegrityError:
            return('ERROR: incorect data.')


api.add_resource(StudentResource, '/students/<int:student_id>/', '/students/<int:student_id>')
api.add_resource(CourseResource, '/courses/<int:course_id>/', '/courses/<int:course_id>')
api.add_resource(GroupResource, '/groups/<int:group_id>/', '/groups/<int:group_id>')

api.add_resource(StudentListResource, '/students/', '/students')
api.add_resource(CourseListResource, '/courses/', '/courses')
api.add_resource(GroupListResource, '/groups/', '/groups')
