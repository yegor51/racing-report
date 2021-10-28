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
from flask import request
from flask_restful import Resource
from .database_functions import *


def return_assertion_massages_decorator(f):
    def warper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AssertionError as e:
            return 'error during operation: ' + str(e)

    return warper


class StudentResource(Resource):
    def get(self, student_id):
        return get_student(student_id)

    @return_assertion_massages_decorator
    def put(self, student_id):
        return put_student(student_id, request.form)

    @return_assertion_massages_decorator
    def delete(self, student_id):
        return delete_student(student_id)


class CourseResource(Resource):
    def get(self, course_id):
        return get_course(course_id)

    @return_assertion_massages_decorator
    def put(self, course_id):
        return put_course(course_id, request.form)

    @return_assertion_massages_decorator
    def delete(self, course_id):
        return delete_course(course_id)


class GroupResource(Resource):
    def get(self, group_id):
        return get_group(group_id)

    @return_assertion_massages_decorator
    def put(self, group_id):
        return put_group(group_id, request.form)

    @return_assertion_massages_decorator
    def delete(self, group_id):
        return delete_group(group_id)


class StudentListResource(Resource):
    def get(self):
        return get_all_students()

    @return_assertion_massages_decorator
    def post(self):
        return post_student(request.form)


class CourseListResource(Resource):
    def get(self):
        return get_all_courses()

    @return_assertion_massages_decorator
    def post(self):
        return post_course(request.form)


class GroupListResource(Resource):
    def get(self):
        return get_all_groups()

    @return_assertion_massages_decorator
    def post(self):
        return post_group(request.form)


api.add_resource(StudentResource, '/students/<int:student_id>/', '/students/<int:student_id>')
api.add_resource(CourseResource, '/courses/<int:course_id>/', '/courses/<int:course_id>')
api.add_resource(GroupResource, '/groups/<int:group_id>/', '/groups/<int:group_id>')

api.add_resource(StudentListResource, '/students/', '/students')
api.add_resource(CourseListResource, '/courses/', '/courses')
api.add_resource(GroupListResource, '/groups/', '/groups')
