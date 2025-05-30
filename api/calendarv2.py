from flask import Blueprint, app, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from datetime import datetime
from model.calendar import Event, initEvents, db  

# New blueprint and API route prefix
calendar_api_v3 = Blueprint('calendar_api_v3', __name__, url_prefix='/api/calendarv3')
api = Api(calendar_api_v3)

# Allowed CORS origins
allowed_origins = ["http://127.0.0.1:4887", "https://zafeera123.github.io"]


from flask import Flask, request, jsonify
from flask_restful import Resource, Api, abort

app = Flask(__name__)
api = Api(app)

# In-memory data stores
EVENTS = {}
SHIPMENTS = {}
TASKS = {}
EMPLOYEES = {}

def abort_if_not_found(data_dict, resource_id, resource_name):
    if resource_id not in data_dict:
        abort(404, message=f"{resource_name} {resource_id} not found")

def validate_fields(data, required_fields):
    missing = [f for f in required_fields if f not in data]
    if missing:
        abort(400, message=f"Missing required fields: {', '.join(missing)}")


class EventList(Resource):

    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def get(self):
        return jsonify(list(EVENTS.values()))

    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def post(self):
        data = request.get_json(force=True)
        required_fields = ["date", "title", "description", "category"]
        validate_fields(data, required_fields)
        event_id = str(len(EVENTS) + 1)
        data['id'] = event_id
        EVENTS[event_id] = data
        return jsonify(data), 201

    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def put(self):
        data = request.get_json(force=True)
        event_id = data.get("id")
        abort_if_not_found(EVENTS, event_id, "Event")
        required_fields = ["date", "title", "description", "category"]
        validate_fields(data, required_fields)
        EVENTS[event_id] = data
        return jsonify(data)

    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def delete(self):
        data = request.get_json(force=True)
        event_id = data.get("id")
        abort_if_not_found(EVENTS, event_id, "Event")
        del EVENTS[event_id]
        return '', 204



class ShipmentList(Resource):
    def get(self):
        return jsonify(list(SHIPMENTS.values()))

    def post(self):
        data = request.get_json(force=True)
        required_fields = ["shipment_date", "item", "quantity", "destination"]
        validate_fields(data, required_fields)
        shipment_id = str(len(SHIPMENTS) + 1)
        data['id'] = shipment_id
        SHIPMENTS[shipment_id] = data
        return jsonify(data), 201

    def put(self):
        data = request.get_json(force=True)
        shipment_id = data.get("id")
        abort_if_not_found(SHIPMENTS, shipment_id, "Shipment")
        required_fields = ["shipment_date", "item", "quantity", "destination"]
        validate_fields(data, required_fields)
        SHIPMENTS[shipment_id] = data
        return jsonify(data)

    def delete(self):
        data = request.get_json(force=True)
        shipment_id = data.get("id")
        abort_if_not_found(SHIPMENTS, shipment_id, "Shipment")
        del SHIPMENTS[shipment_id]
        return '', 204


class TaskList(Resource):
    def get(self):
        return jsonify(list(TASKS.values()))

    def post(self):
        data = request.get_json(force=True)
        required_fields = ["due_date", "title", "priority", "status"]
        validate_fields(data, required_fields)
        task_id = str(len(TASKS) + 1)
        data['id'] = task_id
        TASKS[task_id] = data
        return jsonify(data), 201

    def put(self):
        data = request.get_json(force=True)
        task_id = data.get("id")
        abort_if_not_found(TASKS, task_id, "Task")
        required_fields = ["due_date", "title", "priority", "status"]
        validate_fields(data, required_fields)
        TASKS[task_id] = data
        return jsonify(data)

    def delete(self):
        data = request.get_json(force=True)
        task_id = data.get("id")
        abort_if_not_found(TASKS, task_id, "Task")
        del TASKS[task_id]
        return '', 204


class EmployeeList(Resource):
    def get(self):
        return jsonify(list(EMPLOYEES.values()))

    def post(self):
        data = request.get_json(force=True)
        required_fields = ["name", "position", "department", "email"]
        validate_fields(data, required_fields)
        employee_id = str(len(EMPLOYEES) + 1)
        data['id'] = employee_id
        EMPLOYEES[employee_id] = data
        return jsonify(data), 201

    def put(self):
        data = request.get_json(force=True)
        employee_id = data.get("id")
        abort_if_not_found(EMPLOYEES, employee_id, "Employee")
        required_fields = ["name", "position", "department", "email"]
        validate_fields(data, required_fields)
        EMPLOYEES[employee_id] = data
        return jsonify(data)

    def delete(self):
        data = request.get_json(force=True)
        employee_id = data.get("id")
        abort_if_not_found(EMPLOYEES, employee_id, "Employee")
        del EMPLOYEES[employee_id]
        return '', 204


# Register only list-level resources
api.add_resource(EventList, '/api/events')
api.add_resource(ShipmentList, '/api/shipments')
api.add_resource(TaskList, '/api/tasks')
api.add_resource(EmployeeList, '/api/employees')

