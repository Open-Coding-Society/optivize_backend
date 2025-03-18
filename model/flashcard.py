from sqlalchemy.exc import IntegrityError
from __init__ import app, db
from model.user import User
from model.deck import Deck

class Flashcard(db.Model):
    """
    Flashcard Model
    
    Attributes:
        id (int): Primary key for the flashcard.
        title (str): Title of the flashcard.
        content (str): Content of the flashcard.
        user_id (int): ID of the user who owns this flashcard.
        deck_id (int): ID of the deck to which this flashcard belongs.
    """
    __tablename__ = 'flashcards'

    id = db.Column(db.Integer, primary_key=True)
    _title = db.Column(db.String(255), nullable=False)
    _content = db.Column(db.String(255), nullable=False)
    _user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    _deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=True)

    def __init__(self, title, content, user_id, deck_id=None):
        self._title = title
        self._content = content
        self._user_id = user_id
        self._deck_id = deck_id
        

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            print(f"Flashcard Created: {self._title}, {self._content}")
            return self
        except IntegrityError as e:
            db.session.rollback()
            print(f"IntegrityError while creating flashcard: {e}")
            return None
        except Exception as e:
            db.session.rollback()
            print(f"Unexpected error while creating flashcard: {e}")
            return None

    def read(self):
        return {
            "id": self.id,
            "title": self._title,
            "content": self._content,
            "user_id": self._user_id,
            "deck_id": self._deck_id
        }

    def update(self, data):
        for key, value in data.items():
            if key == "title":
                self._title = value
            if key == "content":
                self._content = value
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def restore(data):
        """
        Restore flashcards from a list of data.

        Args:
            data (list): A list of dictionaries containing flashcard data.
        """
        for card_data in data:
            card_data.pop('id', None)  # Ignore the ID field if present
            user_id = card_data.get("user_id")
            deck_id = card_data.get("deck_id")
            title = card_data.get("title")

            # Check if the flashcard already exists
            flashcard = Flashcard.query.filter_by(_user_id=user_id, _deck_id=deck_id, _title=title).first()
            if flashcard:
                flashcard.update(card_data)
            else:
                flashcard = Flashcard(**card_data)
                flashcard.create()


def initFlashcards():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        print("Flashcards table initialized.")

        # Add test data if the table is empty
        if Flashcard.query.count() == 0:
            user = User.query.first()
            if not user:
                user = User(username='testuser', password='password123')
                db.session.add(user)
                db.session.commit()

            # Example: Create some decks
            deck = Deck(title='Math Flashcards', user_id=user.id)
            db.session.add(deck)
            db.session.commit()

            # Add some flashcards with test data
            flashcards_data = [
                {"title": "What is 2+2?", "content": "4", "user_id": user.id, "deck_id": deck.id},
                {"title": "What is 5+3?", "content": "8", "user_id": user.id, "deck_id": deck.id},
                {"title": "What is 10-6?", "content": "4", "user_id": user.id, "deck_id": deck.id}
            ]

            for card_data in flashcards_data:
                flashcard = Flashcard(**card_data)
                db.session.add(flashcard)

            db.session.commit()
            print("Test data added to Flashcards.")
        else:
            print("Flashcards already exist.")
