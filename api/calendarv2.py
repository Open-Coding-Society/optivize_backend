from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from datetime import datetime
from model.calendar import Event, initEvents, db  

# New blueprint and API route prefix
calendar_api_v3 = Blueprint('calendar_api_v3', __name__, url_prefix='/api/calendarv3')
api = Api(calendar_api_v3)




class CalendarAPIV3(Resource):
    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def get(self):
        try:
            events = Event.query.all()
            events_data = [{
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'start_time': event.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': event.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'category': event.category
            } for event in events]

            return jsonify({'success': True, 'events': events_data})
        except Exception as e:
            return {'message': f'Failed to retrieve events: {str(e)}'}, 500

    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def post(self):
        data = request.get_json()
        required_fields = ['title', 'description', 'start_time', 'end_time', 'category']
        if missing := [f for f in required_fields if f not in data]:
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

            db.session.add(event)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Event created successfully',
                'event_id': event.id
            })

        except Exception as e:
            return {'message': f'Failed to create event: {str(e)}'}, 500

    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
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
            event.start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S') if 'start_time' in data else event.start_time
            event.end_time = datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S') if 'end_time' in data else event.end_time
            event.category = data.get('category', event.category)

            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Event updated successfully',
                'event_id': event.id
            })

        except Exception as e:
            return {'message': f'Failed to update event: {str(e)}'}, 500

    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
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

# Register the new resource
api.add_resource(CalendarAPIV3, '/api/calendarv3/')
