from datetime import datetime
from sqlalchemy.exc import IntegrityError
from __init__ import db, app

class Event(db.Model):
    """
    Event Model for storing calendar events.
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
        """Save the event to the database."""
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError as e:
            db.session.rollback()
            app.logger.error(f"[IntegrityError] Failed to create event: {e}")
            return None
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"[Error] Failed to create event: {e}")
            return None

    def read(self):
        """Return a dictionary representation of the event."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "start_time": self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": self.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            "category": self.category,
            "date_created": self.date_created.strftime('%Y-%m-%d %H:%M:%S')
        }

    def update(self, data):
        """Update the event with a dictionary of values."""
        for key, value in data.items():
            if hasattr(self, key) and key != "id":
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """Delete the event from the database."""
        db.session.delete(self)
        db.session.commit()

def initEvents():
    """
    Initialize the event table and log result.
    """
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("✅ Event table initialized successfully.")
        except Exception as e:
            app.logger.error(f"❌ Failed to initialize event table: {e}")
