from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from datetime import datetime
from model.studylog import Event, db  # Assuming you have an Event model

calendar_api = Blueprint('calendar_api', __name__, url_prefix='/api/calendar')
api = Api(calendar_api)

# Enable CORS
CORS(calendar_api, resources={r"/*": {"origins": ["http://127.0.0.1:4887", "https://zafeera123.github.io"]}},
     supports_credentials=True)

class CalendarAPI(Resource):
    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def get(self):
        """Retrieve all events"""
        try:
            events = Event.query.all()  # Retrieve all events from DB
            events_data = []
            for event in events:
                events_data.append({
                    'id': event.id,
                    'title': event.title,
                    'description': event.description,
                    'start_time': event.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'end_time': event.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'category': event.category
                })
            return jsonify({'success': True, 'events': events_data})

        except Exception as e:
            return {'message': f'Failed to retrieve events: {str(e)}'}, 500

    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def post(self):
        """Create a new event"""
        data = request.get_json()

        required_fields = ['title', 'description', 'start_time', 'end_time', 'category']
        if missing := [f for f in required_fields if f not in data]:
            return {'message': 'Missing required fields', 'missing': missing}, 400

        try:
            # Parse date and time strings into datetime objects
            start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S')

            # Create event and save to DB
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
        """Update an existing event"""
        data = request.get_json()

        if 'id' not in data:
            return {'message': 'Missing event ID'}, 400

        event = Event.query.get(data['id'])
        if not event:
            return {'message': 'Event not found'}, 404

        try:
            # Update event details
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
        """Delete an event"""
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

# Register the API with the Flask app
api.add_resource(CalendarAPI, '/')

