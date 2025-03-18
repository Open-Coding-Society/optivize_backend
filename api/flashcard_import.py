import requests
from flask import Blueprint, jsonify, request
from model.flashcard import Flashcard
from model.deck import Deck  # Import Deck model
from __init__ import db

flashcard_import_api = Blueprint('flashcard_import_api', __name__, url_prefix='/api')

@flashcard_import_api.route('/import-flashcards', methods=['GET'])
def import_flashcards():
    try:
        # Get query parameters with proper handling
        amount = request.args.get('amount', default=10, type=int)  # Default to 10 questions
        difficulty = request.args.get('difficulty', default='medium', type=str)  # Default to medium
        category = request.args.get('category', default=None, type=str)  # Default to None

        # Construct the API URL dynamically
        api_url = f"https://opentdb.com/api.php?amount={amount}&difficulty={difficulty}"
        if category:  # Add the category parameter only if it is provided and valid
            api_url += f"&category={category}"

        # Fetch data from Open Trivia Database
        response = requests.get(api_url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch data from external API"}), 500

        trivia_data = response.json()
        results = trivia_data.get("results", [])

        if not results:
            return jsonify({"error": "No flashcards fetched from the external API"}), 400

        # Create a new deck
        deck_title = f"Imported Deck ({difficulty.capitalize()})"
        if category:
            deck_title += f" - Category {category}"

        user_id = 1  # Replace with actual user_id if authentication is implemented
        new_deck = Deck(title=deck_title, user_id=user_id)
        db.session.add(new_deck)
        db.session.commit()

        flashcards = []
        for item in results:
            question = item.get("question")
            answer = item.get("correct_answer")
            if question and answer:
                flashcard = Flashcard(
                    title=question,
                    content=answer,
                    user_id=user_id,
                    deck_id=new_deck.id  # Associate flashcard with the new deck
                )
                db.session.add(flashcard)
                flashcards.append(flashcard.read())

        db.session.commit()
        return jsonify({
            "message": f"{len(flashcards)} flashcards imported and added to deck '{deck_title}'!",
            "deck": {
                "id": new_deck.id,
                "title": new_deck.title,
                "flashcards": flashcards
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"error": str(e)}), 500
