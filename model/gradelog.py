from sqlalchemy.exc import IntegrityError
from __init__ import app, db
from model.user import User
from datetime import datetime

class GradeLog(db.Model):
    """
    GradeLog Model
    
    Attributes:
        id (int): Primary key for the grade log.
        user_id (int): ID of the user who owns this grade log.
        subject (str): Subject for which the grade is recorded.
        grade (float): Grade received for the subject.
        notes (str): Additional notes about the grade.
        date (datetime): Date when the grade was recorded.
    """
    __tablename__ = 'grade_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, user_id, subject, grade, notes=''):
        self.user_id = user_id
        self.subject = subject
        self.grade = grade
        self.notes = notes

    def create(self):
        """
        Add the current GradeLog instance to the database.
        
        Returns:
            self: The created GradeLog instance if successful, None otherwise.
        """
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def read(self):
        """
        Convert the GradeLog instance to a dictionary.
        
        Returns:
            dict: A dictionary representation of the GradeLog instance.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "subject": self.subject,
            "grade": self.grade,
            "notes": self.notes,
            "date": self.date.strftime('%Y-%m-%d %H:%M:%S')
        }

    def update(self, data):
        """
        Update the GradeLog instance with new data.
        
        Args:
            data (dict): A dictionary containing the new data for the GradeLog instance.
        
        Returns:
            self: The updated GradeLog instance.
        """
        for key, value in data.items():
            if key == "subject":
                self.subject = value
            if key == "grade":
                self.grade = value
            if key == "notes":
                self.notes = value
        db.session.commit()
        return self

    def delete(self):
        """
        Delete the current GradeLog instance from the database.
        """
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def restore(data):
        """
        Restore GradeLog instances from a list of dictionaries.
        
        Args:
            data (list): A list of dictionaries containing the data for GradeLog instances.
        """
        for log_data in data:
            _ = log_data.pop('id', None)
            id = log_data.get("id", None)
            user_id = log_data.get("user_id", None)
            subject = log_data.get("subject", None)
            grade = log_data.get("grade", None)
            notes = log_data.get("notes", None)
            date_str = log_data.get("date", None)
            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S') if date_str else None

            gradelog = GradeLog.query.filter_by(id=id, user_id=user_id, subject=subject, grade=grade, notes=notes, date=date).first()
            if gradelog:
                gradelog.update(log_data)
            else:
                gradelog = GradeLog(user_id=user_id, subject=subject, grade=grade, notes=notes)
                if date:
                    gradelog.date = date
                gradelog.create()

def initGradeLog():
    with app.app_context():
        db.create_all()  # Create all tables
        print("GradeLog table initialized.")

        # Ensure the admin user exists
        admin_user = User.query.filter_by(_uid="admin").first()
        if not admin_user:
            print("Admin user not found. Cannot initialize GradeLogs.")
            return

        # # Define test grade logs
        # grade_logs = [
        #     GradeLog(user_id=admin_user.id, subject='English', grade=80, notes='Analyzed Shakespeare'),
        # ]

        # # Add the test data to the database
        # for log in grade_logs:
        #     db.session.add(log)
        db.session.commit()
        print("Grade logs table initialized with test data.")
