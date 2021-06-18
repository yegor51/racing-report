from .application import api
from .models import StudentModel, CourseModel, GroupModel, students_courses_relation, db
from flask_restful import Resource
from flask import request, jsonify


class StudentResource(Resource):
    def get(self, student_id):
        student = StudentModel.query.filter_by(id=student_id).first()
        courses = db.session.query(students_courses_relation).filter_by(student_id=student_id)
        return jsonify({'first_name': student.first_name,
                        'last_name': student.last_name,
                        'group_id': student.group_id,
                        'courses_ids': [course.course_id for course in courses],
                        })


class CourseResource(Resource):
    def get(self, course_id):
        course = CourseModel.query.filter_by(id=course_id).first()
        students = db.session.query(students_courses_relation).filter_by(course_id=course_id)
        return jsonify({'name': course.name,
                        'description': course.description,
                        'students_ids': [student.student_id for student in students],
                        })


class GroupResource(Resource):
    def get(self, group_id):
        group = GroupModel.query.filter_by(id=group_id).first()
        students = db.session.query(StudentModel).filter_by(group_id=group_id)
        return jsonify({'name': group.name,
                        'students_ids': [student.id for student in students],
                        })


api.add_resource(StudentResource, '/students/<int:student_id>/')
api.add_resource(CourseResource, '/courses/<int:course_id>/')
api.add_resource(GroupResource, '/groups/<int:group_id>/')