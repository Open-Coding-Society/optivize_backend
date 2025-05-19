from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from datetime import datetime
from model.calendar import Event, initEvents, db  

from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_cors import cross_origin
from datetime import datetime
from model.calendar import Event
from __init__ import db

# Create Blueprint and API
calendar_api_v3 = Blueprint('calendar_api_v3', __name__, url_prefix='/api/calendarv3')
api = Api(calendar_api_v3)

# Define allowed origins
allowed_origins = ["http://127.0.0.1:4887", "https://zafeera123.github.io"]

class CalendarAPIV3(Resource):

    @cross_origin(origins=allowed_origins)
    def get(self):
        try:
            events = Event.query.all()
            return jsonify({
                'success': True,
                'events': [event.read() for event in events]
            })
        except Exception as e:
            return {'message': f'Failed to retrieve events: {str(e)}'}, 500

    @cross_origin(origins=allowed_origins)
    def post(self):
        data = request.get_json()
        required = ['title', 'description', 'start_time', 'end_time', 'category']
        missing = [field for field in required if field not in data]
        if missing:
            return {'message': 'Missing required fields', 'missing': missing}, 400

        try:
            start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S')

            event = Event(
                title=data['title'],
                description=data['description'],
                start_time=start_time,
                end_time=end_time,
                category=data['category']
            )
            event.create()

            return jsonify({
                'success': True,
                'message': 'Event created successfully',
                'event': event.read()
            })

        except Exception as e:
            return {'message': f'Failed to create event: {str(e)}'}, 500

    @cross_origin(origins=allowed_origins)
    def put(self):
        data = request.get_json()
        if 'id' not in data:
            return {'message': 'Missing event ID'}, 400

        event = Event.query.get(data['id'])
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

            return jsonify({
                'success': True,
                'message': 'Event updated successfully',
                'event': event.read()
            })

        except Exception as e:
            return {'message': f'Failed to update event: {str(e)}'}, 500

    @cross_origin(origins=allowed_origins)
    def delete(self):
        data = request.get_json()
        if 'id' not in data:
            return {'message': 'Missing event ID'}, 400

        event = Event.query.get(data['id'])
        if not event:
            return {'message': 'Event not found'}, 404

        try:
            db.session.delete(event)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Event deleted successfully',
                'event_id': event.id
            })

        except Exception as e:
            return {'message': f'Failed to delete event: {str(e)}'}, 500

# Register route (no extra '/api/calendarv3/' here, since it's already in Blueprint prefix)
api.add_resource(CalendarAPIV3, '/')
