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
from .application import api
from app.models import StudentModel, GroupModel, CourseModel


def return_assertion_massages_decorator(f):
    def warper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AssertionError as e:
            return 'error during operation: ' + str(e)

    return warper


class ModelResource(Resource):
    model = None

    def get(self, item_id):
        item = self.model.get_item(item_id)
        if not item:
            return {}
        return item.get_params_dict()

    @return_assertion_massages_decorator
    def put(self, item_id):
        item = self.model.get_item(item_id)
        if not item:
            return f'item with id {item_id} not exist in {self.model.__tablename__} model.'
        return item.put_params(**request.form)

    @return_assertion_massages_decorator
    def delete(self, item_id):
        return self.model.delete_item(item_id)


class ModelListResource(Resource):
    model = StudentModel

    def get(self):
        return self.model.get_all_items_params_dict()

    @return_assertion_massages_decorator
    def post(self):
        return self.model.post_item(**request.form)


class StudentResource(ModelResource):
    model = StudentModel


class CourseResource(ModelResource):
    model = CourseModel


class GroupResource(ModelResource):
    model = GroupModel


class StudentListResource(ModelListResource):
    model = StudentModel


class GroupListResource(ModelListResource):
    model = GroupModel


class CourseListResource(ModelListResource):
    model = CourseModel


api.add_resource(StudentResource, '/students/<int:item_id>/', '/students/<int:item_id>')
api.add_resource(CourseResource, '/courses/<int:item_id>/', '/courses/<int:item_id>')
api.add_resource(GroupResource, '/groups/<int:item_id>/', '/groups/<int:item_id>')

api.add_resource(StudentListResource, '/students/', '/students')
api.add_resource(CourseListResource, '/courses/', '/courses')
api.add_resource(GroupListResource, '/groups/', '/groups')
