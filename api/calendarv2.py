from flask import Blueprint, app, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from datetime import datetime
from model.calendar import Event, Employee, Shipment
from __init__ import db

# Blueprint
calendar_api_v3 = Blueprint('calendar_api_v3', __name__, url_prefix='/api/calendarv3')
api = Api(calendar_api_v3)
# Allowed CORS origins
allowed_origins = ["http://127.0.0.1:4887", "https://zafeera123.github.io"]
CORS(app, origins=allowed_origins, supports_credentials=True)
CORS(
    app,
    origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"],
    supports_credentials=True
)
# ---------- EVENTS ----------
class EventAPI(Resource):
    @cross_origin(origins=allowed_origins)
    def get(self):
        try:
            events = Event.query.all()
            return jsonify({'success': True, 'events': [e.read() for e in events]})
        except Exception as e:
            return {'message': f'Error: {str(e)}'}, 500

    @cross_origin(origins=allowed_origins)
    def post(self):
        data = request.get_json()
        required = ['title', 'description', 'start_time', 'end_time', 'category']
        if any(field not in data for field in required):
            return {'message': 'Missing required fields', 'missing': required}, 400
        try:
            event = Event(
                title=data['title'],
                description=data['description'],
                start_time=datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S'),
                end_time=datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S'),
                category=data['category']
            )
            db.session.add(event)
            db.session.commit()
            return jsonify({'success': True, 'event': event.read()})
        except Exception as e:
            return {'message': f'Error: {str(e)}'}, 500

    @cross_origin(origins=allowed_origins)
    def put(self):
        data = request.get_json()
        event = Event.query.get(data.get('id'))
        if not event:
            return {'message': 'Event not found'}, 404
        try:
            event.title = data.get('title', event.title)
            event.description = data.get('description', event.description)
            if 'start_time' in data:
                event.start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S')
            if 'end_time' in data:
                event.end_time = datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S')
            event.category = data.get('category', event.category)
            db.session.commit()
            return jsonify({'success': True, 'event': event.read()})
        except Exception as e:
            return {'message': f'Error: {str(e)}'}, 500

    @cross_origin(origins=allowed_origins)
    def delete(self):
        data = request.get_json()
        event = Event.query.get(data.get('id'))
        if not event:
            return {'message': 'Event not found'}, 404
        try:
            db.session.delete(event)
            db.session.commit()
            return jsonify({'success': True, 'event_id': event.id})
        except Exception as e:
            return {'message': f'Error: {str(e)}'}, 500

# ---------- EMPLOYEES ----------
class EmployeeAPI(Resource):
    @cross_origin(origins=allowed_origins)
    def get(self):
        try:
            employees = Employee.query.all()
            return jsonify({'success': True, 'employees': [e.read() for e in employees]})
        except Exception as e:
            return {'message': f'Error: {str(e)}'}, 500

    @cross_origin(origins=allowed_origins)
    def post(self):
        data = request.get_json()
        try:
            employee = Employee(
                name=data['name'],
                position=data['position'],
                work_time=data['work_time']
            )
            db.session.add(employee)
            db.session.commit()
            return jsonify({'success': True, 'employee': employee.read()})
        except Exception as e:
            return {'message': f'Error: {str(e)}'}, 500

    @cross_origin(origins=allowed_origins)
    def put(self):
        data = request.get_json()
        employee = Employee.query.get(data.get('id'))
        if not employee:
            return {'message': 'Employee not found'}, 404
        try:
            employee.name = data.get('name', employee.name)
            employee.position = data.get('position', employee.position)
            employee.work_time = data.get('work_time', employee.work_time)
            db.session.commit()
            return jsonify({'success': True, 'employee': employee.read()})
        except Exception as e:
            return {'message': f'Error: {str(e)}'}, 500

    @cross_origin(origins=allowed_origins)
    def delete(self):
        data = request.get_json()
        employee = Employee.query.get(data.get('id'))
        if not employee:
            return {'message': 'Employee not found'}, 404
        try:
            db.session.delete(employee)
            db.session.commit()
            return jsonify({'success': True, 'employee_id': employee.id})
        except Exception as e:
            return {'message': f'Error: {str(e)}'}, 500

# ---------- SHIPMENTS ----------
class ShipmentAPI(Resource):
    @cross_origin(origins=allowed_origins)
    def get(self):
        try:
            shipments = Shipment.query.all()
            return jsonify({'success': True, 'shipments': [s.read() for s in shipments]})
        except Exception as e:
            return {'message': f'Error: {str(e)}'}, 500

    @cross_origin(origins=allowed_origins)
    def post(self):
        data = request.get_json()
        try:
            shipment = Shipment(
                inventory=data['inventory'],
                amount=data['amount'],
                transport_method=data['transport_method'],
                shipment_time=data['shipment_time']
            )
            db.session.add(shipment)
            db.session.commit()
            return jsonify({'success': True, 'shipment': shipment.read()})
        except Exception as e:
            return {'message': f'Error: {str(e)}'}, 500

    @cross_origin(origins=allowed_origins)
    def put(self):
        data = request.get_json()
        shipment = Shipment.query.get(data.get('id'))
        if not shipment:
            return {'message': 'Shipment not found'}, 404
        try:
            shipment.inventory = data.get('inventory', shipment.inventory)
            shipment.amount = data.get('amount', shipment.amount)
            shipment.transport_method = data.get('transport_method', shipment.transport_method)
            shipment.shipment_time = data.get('shipment_time', shipment.shipment_time)
            db.session.commit()
            return jsonify({'success': True, 'shipment': shipment.read()})
        except Exception as e:
            return {'message': f'Error: {str(e)}'}, 500

    @cross_origin(origins=allowed_origins)
    def delete(self):
        data = request.get_json()
        shipment = Shipment.query.get(data.get('id'))
        if not shipment:
            return {'message': 'Shipment not found'}, 404
        try:
            db.session.delete(shipment)
            db.session.commit()
            return jsonify({'success': True, 'shipment_id': shipment.id})
        except Exception as e:
            return {'message': f'Error: {str(e)}'}, 500
class CalendarTableAPI(Resource):
    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def get(self):
        try:
            employees = Employee.query.order_by(Employee.name.asc()).all()
            shipments = Shipment.query.order_by(Shipment.delivery_date.asc()).all()

            return jsonify({
                "employees": [e.read() for e in employees],
                "shipments": [s.read() for s in shipments]
            })

        except Exception as e:
            return {'message': f'Failed to fetch calendar data: {str(e)}'}, 500


# Register all API routes
api.add_resource(EventAPI, '/events')
api.add_resource(EmployeeAPI, '/employees')
api.add_resource(ShipmentAPI, '/shipments')
api.add_resource(CalendarTableAPI, '/table')
