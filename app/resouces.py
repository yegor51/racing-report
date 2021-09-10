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
                'courses_ids' - list of ids of student courses

    CourseResource:
        get method:
             return data about course by course id from the `courses` table in json
             format.
             json keys:
                'name' - str, name of the course
                'description' - str, description of the course
                'students_ids' - list of ids of students, joined to the course

    GroupResource:
        get method:
            return data about group by group id from the 'groups' table in json format.
            json keys:
                'name' - str, name of the group
                'students_ids' - list of ids of all students in this group"""
from .application import api, db
from .models import StudentModel, CourseModel, GroupModel, students_courses_relation
from flask_restful import Resource
from flask import jsonify


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


api.add_resource(StudentResource, '/students/<int:student_id>/')
api.add_resource(CourseResource, '/courses/<int:course_id>/')
api.add_resource(GroupResource, '/groups/<int:group_id>/')