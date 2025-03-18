import logging
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from __init__ import app, db
from model.user import User

class StudyLog(db.Model):
    """
    This class defines the 'studylog' table structure and 
    provides methods for creating, reading, updating, and 
    deleting study log records.
    """

    __tablename__ = 'studylog'

    # Columns in the 'studylog' table
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # references 'users' table
    subject = db.Column(db.String(100), nullable=False)      # subject of study
    hours_studied = db.Column(db.Float, nullable=False)      # amount of time studied (in hours)
    notes = db.Column(db.Text)                               # any additional notes
    date = db.Column(db.DateTime, default=lambda: datetime.now())

    def __init__(self, user_id, subject, hours_studied, notes='', date=None):
        """
        Constructor initializes the study log with user ID, subject, 
        hours studied, and notes. The date can be manually specified; 
        otherwise, current time is used.
        """
        self.user_id = user_id
        self.subject = subject
        self.hours_studied = hours_studied
        self.notes = notes
        self.date = date or datetime.now()

    def __repr__(self):
        """
        Returns a string representation useful for debugging/logging.
        """
        return (f"StudyLog(id={self.id}, user_id={self.user_id}, "
                f"subject={self.subject}, hours_studied={self.hours_studied}, notes={self.notes})")

    def create(self):
        """
        Adds the current StudyLog record to the session and commits it to the database.
        Catches and logs IntegrityError exceptions (e.g., foreign key issues).
        """
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            logging.warning(f"IntegrityError: Could not create studylog with subject '{self.subject}' due to {str(e)}.")
            return None
        return self

    def read(self):
        """
        Converts the StudyLog object into a dictionary for JSON serialization.
        Includes user_id from the 'users' table (linked by ForeignKey).
        """
        user = User.query.get(self.user_id)
        data = {
            "id": self.id,
            "user_id": user.id if user else None,
            "subject": self.subject,
            "hours_studied": self.hours_studied,
            "notes": self.notes,
            "date": self.date.strftime('%Y-%m-%d %H:%M:%S')
        }
        return data

    def update(self, data):
        """
        Updates this StudyLog record with values from a dictionary (e.g., from an API request).
        Commits the changes if successful, or rolls back if an error occurs.
        """
        for key, value in data.items():
            setattr(self, key, value)  # set each attribute to the new value
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self):
        """
        Deletes this StudyLog record from the database.
        Rolls back if an exception occurs.
        """
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def restore(data):
        """
        Restores StudyLog data from a list of dictionaries (e.g., JSON backup).
        Skips certain entries or invalid data. Ensures valid fields exist before 
        creating new records or updates. Handles errors and logs warnings.
        """
        for log_data in data:
            # Skip logs with IDs 1, 2, or 3
            if log_data.get('id') in [1, 2, 3]:
                logging.info(f"Skipping log with id {log_data['id']}")
                continue

            # Remove 'id' to allow DB to auto-generate an ID
            log_data.pop('id', None)

            # Convert date string to datetime object if present
            date_str = log_data.get("date")
            if date_str:
                try:
                    log_data["date"] = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    logging.warning(f"Invalid date format for '{date_str}'. Skipping log.")
                    continue  # skip invalid entries

            # Check for required fields (user_id, subject, hours_studied)
            required_fields = ["user_id", "subject", "hours_studied"]
            if not all(field in log_data and log_data[field] for field in required_fields):
                logging.warning(f"Missing required fields in log data: {log_data}. Skipping log.")
                continue

            # Create and insert new StudyLog record
            try:
                new_studylog = StudyLog(**log_data)
                db.session.add(new_studylog)
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                logging.warning(f"IntegrityError: Could not restore log due to {str(e)}.")
            except Exception as e:
                db.session.rollback()
                logging.warning(f"Error restoring log: {str(e)}.")

def initStudyLog():
    """
    Initializes the StudyLog table and inserts some default records 
    if the table is empty. Useful for quick testing or seeding the DB.
    """
    with app.app_context():
        # Create the table if it doesn't exist
        db.create_all()
        
        # Example seed data
        studylogs = [
            StudyLog(user_id=1, subject='Math', hours_studied=2.5, notes='Reviewed algebra and geometry.'),
            StudyLog(user_id=1, subject='Science', hours_studied=1.5, notes='Studied physics and chemistry.'),
            StudyLog(user_id=2, subject='History', hours_studied=3.0, notes='Read about World War II.'),
        ]
        
        # Attempt to create each study log record
        for studylog in studylogs:
            try:
                studylog.create()
                print(f"Record created: {repr(studylog)}")
            except IntegrityError:
                db.session.rollback()
                logging.warning(f"IntegrityError: Could not add studylog with subject '{studylog.subject}' due to missing user_id.")
                