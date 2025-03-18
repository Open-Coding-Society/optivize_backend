# from flask import Blueprint, request, jsonify, Response, g
# from flask_restful import Api, Resource
from __init__ import db, app  # Import `app` for context management
# from api.jwt_authorize import token_required

# # Blueprint for Leaderboard API
# leaderboard_api = Blueprint('leaderboard_api', __name__, url_prefix='/api')

# # Flask-RESTful API object
# api = Api(leaderboard_api)

# LeaderboardEntry Model
class LeaderboardEntry(db.Model):
    __tablename__ = 'leaderboard'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    def create(self):
        db.session.add(self)
        db.session.commit()

    def read(self):
        return {"id": self.id, "name": self.name, "score": self.score}

    def update(self, newScore):
        self.score = newScore
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()



# Initialize the Leaderboard Table
def initLeaderboard():
    """
    Initialize the leaderboard table and populate it with default data.
    """
    with app.app_context():  # Use Flask app context
        db.create_all()  # Create all tables
        print("Leaderboard table initialized.")

        # Add default data if the table is empty
        if LeaderboardEntry.query.first() is None:
            default_entries = [
                {"name": "Alice", "score": 5},
                {"name": "Bob", "score": 6},
                {"name": "Charlie", "score": 7},
            ]
            for entry in default_entries:
                new_entry = LeaderboardEntry(name=entry['name'], score=entry['score'])
                db.session.add(new_entry)
            try:
                db.session.commit()
                print("Default leaderboard entries added.")
            except Exception as e:
                db.session.rollback()
                print(f"Error initializing leaderboard data: {e}")
        else:
            print("Leaderboard table already contains data.")



            