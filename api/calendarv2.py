from flask import Blueprint, app, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from datetime import datetime
from model.calendar import Event, Task, Shipment, Employee, initEvents, db  

# New blueprint and API route prefix
calendar_api_v3 = Blueprint('calendar_api', __name__, url_prefix='/api')

"""
The Api object is connected to the Blueprint object to define the API endpoints.
- The API object is used to add resources to the API.
- The objects added are mapped to code that contains the actions for the API.
- For more information, refer to the API docs: https://flask-restful.readthedocs.io/en/latest/api.html
"""
api = Api(calendar_api_v3)

# Allowed CORS origins
allowed_origins = ["http://127.0.0.1:4887", "https://zafeera123.github.io"]

def abort_if_not_found(data_dict, resource_id, resource_name):
    if resource_id not in data_dict:
        abort(404, message=f"{resource_name} {resource_id} not found")

def validate_fields(data, required_fields):
    missing = [f for f in required_fields if f not in data]
    if missing:
        abort(400, message=f"Missing required fields: {', '.join(missing)}")

def get_user_data(model_class, uid):
    """Helper function to get user-specific data"""
    return [item.read() for item in model_class.query.filter_by(uid=uid).all()]

class EventList(Resource):
    @cross_origin(origins=allowed_origins, supports_credentials=True)
    def get(self):
        uid = request.args.get('uid')
        if not uid:
            return jsonify({"error": "User ID (uid) is required"}), 400
        return jsonify(get_user_data(Event, uid))

    @cross_origin(origins=allowed_origins, supports_credentials=True)
    def post(self):
        data = request.get_json(force=True)
        required_fields = ["uid", "date", "title", "description", "category"]
        validate_fields(data, required_fields)
        
        event = Event(
            uid=data['uid'],
            title=data['title'],
            description=data['description'],
            start_time=datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S'),
            end_time=datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S'),
            category=data['category']
        )
        created_event = event.create()
        return jsonify(created_event.read()), 201

    @cross_origin(origins=allowed_origins, supports_credentials=True)
    def put(self):
        data = request.get_json(force=True)
        event_id = data.get("id")
        event = Event.query.get(event_id)
        if not event:
            abort(404, message=f"Event {event_id} not found")
        if event.uid != data.get('uid'):
            abort(403, message="Unauthorized to modify this event")
        event.update(data)
        return jsonify(event.read())

    @cross_origin(origins=allowed_origins, supports_credentials=True)
    def delete(self):
        data = request.get_json(force=True)
        event_id = data.get("id")
        event = Event.query.get(event_id)
        if not event:
            abort(404, message=f"Event {event_id} not found")
        if event.uid != data.get('uid'):
            abort(403, message="Unauthorized to delete this event")
        event.delete()
        return '', 204

class TaskList(Resource):
    @cross_origin(origins=allowed_origins, supports_credentials=True)
    def get(self):
        uid = request.args.get('uid')
        if not uid:
            return jsonify({"error": "User ID (uid) is required"}), 400
        return jsonify(get_user_data(Task, uid))

    @cross_origin(origins=allowed_origins, supports_credentials=True)
    def post(self):
        data = request.get_json(force=True)
        required_fields = ["uid", "title", "description", "due_date", "priority", "status"]
        validate_fields(data, required_fields)
        
        task = Task(
            uid=data['uid'],
            title=data['title'],
            description=data['description'],
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d %H:%M:%S'),
            priority=data['priority'],
            status=data['status'],
            employee=data.get('employee')
        )
        created_task = task.create()
        return jsonify(created_task.read()), 201

    @cross_origin(origins=allowed_origins, supports_credentials=True)
    def put(self):
        data = request.get_json(force=True)
        task_id = data.get("id")
        task = Task.query.get(task_id)
        if not task:
            abort(404, message=f"Task {task_id} not found")
        if task.uid != data.get('uid'):
            abort(403, message="Unauthorized to modify this task")
        task.update(data)
        return jsonify(task.read())

    @cross_origin(origins=allowed_origins, supports_credentials=True)
    def delete(self):
        data = request.get_json(force=True)
        task_id = data.get("id")
        task = Task.query.get(task_id)
        if not task:
            abort(404, message=f"Task {task_id} not found")
        if task.uid != data.get('uid'):
            abort(403, message="Unauthorized to delete this task")
        task.delete()
        return '', 204

class ShipmentList(Resource):
    @cross_origin(origins=allowed_origins, supports_credentials=True)
    def get(self):
        uid = request.args.get('uid')
        if not uid:
            return jsonify({"error": "User ID (uid) is required"}), 400
        return jsonify(get_user_data(Shipment, uid))

    @cross_origin(origins=allowed_origins, supports_credentials=True)
    def post(self):
        data = request.get_json(force=True)
        required_fields = ["uid", "inventory", "amount", "transport_method", "shipment_time"]
        validate_fields(data, required_fields)
        
        shipment = Shipment(
            uid=data['uid'],
            inventory=data['inventory'],
            amount=data['amount'],
            transport_method=data['transport_method'],
            shipment_time=data['shipment_time'],
            destination=data.get('destination')
        )
        created_shipment = shipment.create()
        return jsonify(created_shipment.read()), 201

    @cross_origin(origins=allowed_origins, supports_credentials=True)
    def put(self):
        data = request.get_json(force=True)
        shipment_id = data.get("id")
        shipment = Shipment.query.get(shipment_id)
        if not shipment:
            abort(404, message=f"Shipment {shipment_id} not found")
        if shipment.uid != data.get('uid'):
            abort(403, message="Unauthorized to modify this shipment")
        shipment.update(data)
        return jsonify(shipment.read())

    @cross_origin(origins=allowed_origins, supports_credentials=True)
    def delete(self):
        data = request.get_json(force=True)
        shipment_id = data.get("id")
        shipment = Shipment.query.get(shipment_id)
        if not shipment:
            abort(404, message=f"Shipment {shipment_id} not found")
        if shipment.uid != data.get('uid'):
            abort(403, message="Unauthorized to delete this shipment")
        shipment.delete()
        return '', 204

class EmployeeList(Resource):
    @cross_origin(origins=allowed_origins, supports_credentials=True)
    def get(self):
        uid = request.args.get('uid')
        if not uid:
            return jsonify({"error": "User ID (uid) is required"}), 400
        return jsonify(get_user_data(Employee, uid))

    @cross_origin(origins=allowed_origins, supports_credentials=True)
    def post(self):
        data = request.get_json(force=True)
        required_fields = ["uid", "name", "position", "work_time"]
        validate_fields(data, required_fields)
        
        employee = Employee(
            uid=data['uid'],
            name=data['name'],
            position=data['position'],
            work_time=data['work_time']
        )
        created_employee = employee.create()
        return jsonify(created_employee.read()), 201

    @cross_origin(origins=allowed_origins, supports_credentials=True)
    def put(self):
        data = request.get_json(force=True)
        employee_id = data.get("id")
        employee = Employee.query.get(employee_id)
        if not employee:
            abort(404, message=f"Employee {employee_id} not found")
        if employee.uid != data.get('uid'):
            abort(403, message="Unauthorized to modify this employee")
        employee.update(data)
        return jsonify(employee.read())

    @cross_origin(origins=allowed_origins, supports_credentials=True)
    def delete(self):
        data = request.get_json(force=True)
        employee_id = data.get("id")
        employee = Employee.query.get(employee_id)
        if not employee:
            abort(404, message=f"Employee {employee_id} not found")
        if employee.uid != data.get('uid'):
            abort(403, message="Unauthorized to delete this employee")
        employee.delete()
        return '', 204

# Register resources
api.add_resource(EventList, '/events')
api.add_resource(TaskList, '/tasks')
api.add_resource(ShipmentList, '/shipments')
api.add_resource(EmployeeList, '/employees')

