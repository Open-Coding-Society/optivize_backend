from sqlalchemy.exc import IntegrityError
from datetime import datetime
from __init__ import app, db

class Event(db.Model):
    """
    Event Model for storing user-inputted calendar events
    
    Attributes:
        id (int): Primary key
        title (str): Title of the event
        description (str): Description of the event
        start_time (datetime): Start date and time of the event
        end_time (datetime): End date and time of the event
        category (str): Category of the event (optional)
        date_created (datetime): When the event was created
    """
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, title, description, start_time, end_time, category=None):
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.category = category

    def create(self):
        """Create a new event record"""
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError as e:
            db.session.rollback()
            app.logger.error(f"IntegrityError while saving event: {e}")
            return None
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Unexpected error while saving event: {e}")
            return None

    def read(self):
        """Return dictionary representation of the event"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "category": self.category,
            "date_created": self.date_created.isoformat() if self.date_created else None
        }

    def update(self, data):
        """Update event fields with provided dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """Delete this event record"""
        db.session.delete(self)
        db.session.commit()
        return None

def initEvents():
    """Initialize the database table for events"""
    with app.app_context():
        db.create_all()
        app.logger.info("Event table initialized")
