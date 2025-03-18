from sqlalchemy.exc import IntegrityError
from __init__ import db
from flask import current_app
from sqlalchemy.orm import relationship

class Deck(db.Model):
    """
    Deck Model

    Attributes:
        id (int): Primary key for the deck.
        title (str): Title of the deck.
        user_id (int): ID of the user who owns this deck.
    """
    __tablename__ = 'decks'

    id = db.Column(db.Integer, primary_key=True)
    _title = db.Column(db.String(255), nullable=False)
    _user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship with Flashcard
    flashcards = relationship('Flashcard', cascade="all, delete", backref='deck')

    # Constructor
    def __init__(self, title, user_id):
        self._title = title
        self._user_id = user_id

    # Property for title
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    # Property for user_id
    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    # Create method
    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            print(f"Deck created: {self.title}")
            return self
        except IntegrityError as e:
            db.session.rollback()
            print(f"IntegrityError while creating deck: {e}")
            return None
        except Exception as e:
            db.session.rollback()
            print(f"Unexpected error while creating deck: {e}")
            return None

    # Read method
    def read(self):
        return {
            "id": self.id,
            "title": self.title,  # Access via property
            "user_id": self.user_id,  # Access via property
        }

    # Delete method
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def restore(data):
        """
        Restore decks from a list of data.

        Args:
            data (list): A list of dictionaries containing deck data.
        """
        for deck_data in data:
            deck_data.pop('id', None)  # Ignore the ID field if present
            user_id = deck_data.get("user_id")
            title = deck_data.get("title")

            # Check if the deck already exists
            deck = Deck.query.filter_by(_user_id=user_id, _title=title).first()
            if deck:
                print(f"Deck already exists: {title}")
            else:
                new_deck = Deck(**deck_data)
                new_deck.create()

# Initialization function
def initDecks():
    with current_app.app_context():
        db.create_all()
        print("Decks table initialized.")