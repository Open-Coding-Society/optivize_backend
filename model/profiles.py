from sqlite3 import IntegrityError
from sqlalchemy import Text
from __init__ import app, db
from model.user import User

class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), nullable=False)  # User's name
    _classes = db.Column(db.JSON, nullable=False)  # JSON column to store classes
    _favorite_class = db.Column(db.String(255), nullable=False)  # Favorite class
    _grade = db.Column(db.String(10), nullable=False)  # Grade

    def __init__(self, name, classes, favorite_class, grade):
        self._name = name
        self._classes = classes if classes else []
        self._favorite_class = favorite_class
        self._grade = grade

    @property
    def name(self):
        return self._name

    @property
    def classes(self):
        return self._classes

    @property
    def favorite_class(self):
        return self._favorite_class

    @property
    def grade(self):
        return self._grade

    def add_class(self, class_name):
        if class_name not in self._classes:
            self._classes.append(class_name)
            db.session.commit()
            return True
        return False

    def remove_class(self, class_name):
        if class_name in self._classes:
            self._classes.remove(class_name)
            db.session.commit()
            return True
        return False

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def read(self):
        return {
            'id': self.id,
            'name': self.name,
            'classes': self.classes,
            'favorite_class': self.favorite_class,
            'grade': self.grade,
        }

    def update(self, inputs):
        if not isinstance(inputs, dict):
            return self
        self._name = inputs.get("name", self._name)
        self._classes = inputs.get("classes", self._classes)
        self._favorite_class = inputs.get("favorite_class", self._favorite_class)
        self._grade = inputs.get("grade", self._grade)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def restore(data):
        for profile_data in data:
            _ = profile_data.pop('id', None)  # Remove 'id' to avoid conflicts
            name = profile_data.get("name")
            profile = Profile.query.filter_by(_name=name).first()
            if profile:
                profile.update(profile_data)
            else:
                profile = Profile(**profile_data)
                profile.create()

# Initialization function to add test data
def initProfiles():
    with app.app_context():
        db.create_all()

        p1 = Profile(name='Arush Shah', classes=['Math', 'Science', 'History'],
                     favorite_class='Science', grade='A')
        p2 = Profile(name='Jackson Patrick', classes=['Art', 'Music', 'Literature'],
                     favorite_class='Art', grade='A+')
        p3 = Profile(name='Armaghan Zarak', classes=['Computer Science', 'Physics', 'Biology'],
                     favorite_class='Computer Science', grade='B+')

        for profile in [p1, p2, p3]:
            try:
                profile.create()
                print(f"Added profile {profile.name} successfully.")
            except IntegrityError as e:
                db.session.rollback()
                print(f"Error adding profile {profile.name}: {e}")
