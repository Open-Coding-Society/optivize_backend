from sqlalchemy.exc import IntegrityError
from __init__ import app, db
from model.user import User

class CalendarEvent(db.Model):
    """
    CalendarEvent Model
    
    Attributes:
        id (int): Primary key for the event.
        title (str): Title of the event.
        start_time (str): Start date (ISO format) of the event.
        end_time (str): End date (ISO format) of the event.
        description (str): Description of the event.
        user_id (int): ID of the user who owns this event.
    """
    __tablename__ = 'calendar_events'

    id = db.Column(db.Integer, primary_key=True)
    _title = db.Column(db.String(255), nullable=False)
    _start_time = db.Column(db.String(255), nullable=False)
    _end_time = db.Column(db.String(255), nullable=True)
    _description = db.Column(db.String(500), nullable=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, title, start_time, user_id, end_time=None, description=None):
        self._title = title
        self._start_time = start_time
        self._end_time = end_time
        self._description = description
        self._user_id = user_id

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            print(f"Event Created: {self._title}, {self._start_time}")
        except IntegrityError:
            db.session.rollback()
            return None
        return self

    def read(self):
        return {
            "id": self.id,
            "title": self._title,
            "start_time": self._start_time,
            "end_time": self._end_time,
            "description": self._description,
            "user_id": self._user_id
        }

    def update(self, data):
        for key, value in data.items():
            if key == "title":
                self._title = value
            if key == "start_time":
                self._start_time = value
            if key == "end_time":
                self._end_time = value
            if key == "description":
                self._description = value
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()


def initCalendarEvents():
    """
    Initialize the calendar_events table.
    """
    with app.app_context():
        db.create_all()
        print("Calendar events table initialized.")


# API Endpoints
@app.route('/calendar', methods=['POST'])
def create_event():
    data = request.get_json()
    try:
        user_id = data.get('user_id')
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        event = CalendarEvent(
            title=data['title'],
            start_time=data['start_time'],
            user_id=user_id,
            end_time=data.get('end_time'),
            description=data.get('description', "")
        )
        event.create()
        return event.read(), 201
    except Exception as e:
        return {"error": str(e)}, 400


@app.route('/calendar', methods=['GET'])
def get_events():
    user_id = request.args.get('user_id')
    if not user_id:
        return {"error": "Missing user_id parameter"}, 400
    events = CalendarEvent.query.filter_by(_user_id=user_id).all()
    return [event.read() for event in events], 200


@app.route('/calendar/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.get_json()
    event = CalendarEvent.query.get(event_id)
    if not event:
        return {"error": "Event not found"}, 404
    event.update(data)
    return event.read(), 200


@app.route('/calendar/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = CalendarEvent.query.get(event_id)
    if not event:
        return {"error": "Event not found"}, 404
    event.delete()
    return {"message": "Event deleted successfully"}, 200
