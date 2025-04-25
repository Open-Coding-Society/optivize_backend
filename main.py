# imports from flask
import json
from __init__ import app, db
import google.generativeai as genai
from __init__ import app, db
import requests
import json
import os
from urllib.parse import urljoin, urlparse
from flask import abort, redirect, render_template, request, send_from_directory, url_for, jsonify
from flask_login import current_user, login_user, logout_user
from flask.cli import AppGroup
from flask_login import current_user, login_required
from flask import current_app
from flask import g
from api.jwt_authorize import token_required
from werkzeug.security import generate_password_hash
import shutil
from flask_cors import CORS  # Import CORS
from flask import Blueprint, jsonify
from api.flashcard import flashcard_api
from model.channel import Channel
from api.deck import deck_api
import numpy as np
import random


# import "objects" from "this" project
from __init__ import app, db, login_manager  # Key Flask objects 

# API endpoints
from api.user import user_api 
from api.pfp import pfp_api
from api.nestImg import nestImg_api  # Custom format
from api.post import post_api
from api.channel import channel_api
from api.group import group_api
from api.section import section_api
from api.nestPost import nestPost_api  # Custom format
from api.messages_api import messages_api  # Messages
from api.flashcard import flashcard_api
from api.vote import vote_api
from api.studylog import cookie_api
from api.gradelog import gradelog_api
from api.profile import profile_api
from api.tips import tips_api
from api.leaderboard import leaderboard_api




# database Initialization functions
from model.user import User, initUsers
from model.section import Section, initSections
from model.group import Group, initGroups
from model.channel import Channel, initChannels
from model.post import Post, initPosts
from model.nestPost import NestPost, initNestPosts
from model.vote import Vote, initVotes
from model.flashcard import Flashcard, initFlashcards
from model.studylog import CookieSalesPrediction
from model.gradelog import initGradeLog
from model.profiles import Profile, initProfiles
from model.chatlog import ChatLog, initChatLogs
from model.gradelog import GradeLog
from model.deck import Deck, initDecks

from model.leaderboard import LeaderboardEntry, initLeaderboard
# server only Views

# register URIs for API endpoints
app.register_blueprint(messages_api)
app.register_blueprint(user_api)
app.register_blueprint(pfp_api) 
# app.register_blueprint(post_api)
app.register_blueprint(channel_api)
app.register_blueprint(group_api)
app.register_blueprint(section_api)
app.register_blueprint(nestPost_api)
app.register_blueprint(nestImg_api)
app.register_blueprint(vote_api)
app.register_blueprint(flashcard_api)
app.register_blueprint(cookie_api)
app.register_blueprint(gradelog_api)
app.register_blueprint(profile_api)
app.register_blueprint(tips_api)
app.register_blueprint(deck_api)
app.register_blueprint(leaderboard_api)



# Tell Flask-Login the view function name of your login route
login_manager.login_view = "login"

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login', next=request.path))
 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Helper function to check if the URL is safe for redirects
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    next_page = request.args.get('next', '') or request.form.get('next', '')
    if request.method == 'POST':
        user = User.query.filter_by(_uid=request.form['username']).first()
        if user and user.is_password(request.form['password']):
            login_user(user)
            if not is_safe_url(next_page):
                return abort(400)
            return redirect(next_page or url_for('index'))
        else:
            error = 'Invalid username or password.'
    return render_template("login.html", error=error, next=next_page)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Routes for grade logger
@app.route('/api/grade-tracker/log', methods=['POST'])
def log_grade():
    """
    Log a new grade for a user.
    """
    try:
        data = request.json
        new_log = gradelog(
            user_id=data['user_id'],
            subject=data['subject'],
            grade=data['grade'],  # Changed from hours_studied to grade
            notes=data.get('notes', '')
        )
        db.session.add(new_log)
        db.session.commit()
        return jsonify({'message': 'Grade logged successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/grade-tracker/progress/<int:user_id>', methods=['GET'])
def get_grade_progress(user_id):
    """
    Retrieve all grades for a specific user.
    """
    try:
        logs = gradelog.query.filter_by(user_id=user_id).all()
        data = [
            {
                'subject': log.subject,
                'grade': log.grade,  # Changed from hours to grade
                'date': log.date.strftime('%Y-%m-%d')
            }
            for log in logs
        ]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def index():
    print("Home:", current_user)
    return render_template("index.html")

@app.route('/users/table')
@login_required
def utable():
    users = User.query.all()
    return render_template("utable.html", user_data=users)

@app.route('/users/table2')
@login_required
def u2table():
    users = User.query.all()
    return render_template("u2table.html", user_data=users)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@app.route('/users/delete/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.delete()
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'error': 'User not found'}), 404

@app.route('/users/reset_password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    if current_user.role != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.update({"password": app.config['DEFAULT_PASSWORD']}):
        return jsonify({'message': 'Password reset successfully'}), 200
    return jsonify({'error': 'Password reset failed'}), 500

@app.route('/api/id', methods=['GET'])
def get_id():
    return jsonify({"message": "API is working!"}), 200

@app.route("/flashcards")
@login_required
def flashcard_page():
    """Render the Flashcard Management page"""
    if current_user.role == "Admin":
        flashcards = Flashcard.query.all()  # Admins see all flashcards
    else:
        flashcards = Flashcard.query.filter_by(_user_id=current_user.id).all()  # Users see only their own flashcards

    print(f"Flashcards fetched: {len(flashcards)}")  # Debugging log
    for flashcard in flashcards:
        print(flashcard.read())  # Debugging log

    return render_template("flashcard_table.html", flashcards=flashcards)



# Custom CLI Commands
custom_cli = AppGroup('custom', help='Custom commands')


@custom_cli.command('generate_data')
def generate_data():
    initUsers()
    initSections()
    initGroups()
    initFlashcards()
    initDecks()
    # initChannels()
    # initPosts()
    initDecks()
    initChatLogs()
    initProfiles()
    CookieSalesPrediction()
    initLeaderboard()


def backup_database(db_uri, backup_uri):
    if backup_uri:
        db_path = db_uri.replace('sqlite:///', 'instance/')
        backup_path = backup_uri.replace('sqlite:///', 'instance/')
        shutil.copyfile(db_path, backup_path)
        print(f"Database backed up to {backup_path}")
    else:
        print("Backup not supported for production database.")

def extract_data():
    data = {}
    with app.app_context():
        data['users'] = [user.read() for user in User.query.all()]
        data['sections'] = [section.read() for section in Section.query.all()]
        data['gradelog'] = [log.read() for log in GradeLog.query.all()]
        data['groups'] = [group.read() for group in Group.query.all()]
        data['decks'] = [deck.read() for deck in Deck.query.all()]
#        data['channels'] = [channel.read() for channel in Channel.query.all()]
    #    data['posts'] = [post.read() for post in Post.query.all()]
        data['studylogs'] = [log.read() for log in StudyLog.query.all()]
        data['profiles'] = [log.read() for log in Profile.query.all()]
        data['flashcards'] = [log.read() for log in Flashcard.query.all()]
        data['chatlog'] = [log.read() for log in ChatLog.query.all()]
            

    return data

def save_data_to_json(data, directory='backup'):
    if not os.path.exists(directory):
        os.makedirs(directory)
    for table, records in data.items():
        with open(os.path.join(directory, f'{table}.json'), 'w') as f:
            json.dump(records, f)
    print(f"Data backed up to {directory} directory.")

def load_data_from_json(directory='backup'):
    data = {}
    for table in ['users', 'sections', 'groups', 'gradelog', 'studylogs', 'profiles', 'flashcards', 'decks']:
        with open(os.path.join(directory, f'{table}.json'), 'r') as f:
            data[table] = json.load(f)
    return data

def restore_data(data):
    with app.app_context():
        users = User.restore(data['users'])
        _ = Section.restore(data['sections'])
        _ = Group.restore(data['groups'], users)
        _ = Deck.restore(data['decks'])
        # _ = Channel.restore(data['channels'])
        #  _ = Post.restore(data['posts'])
        _ = StudyLog.restore(data['studylogs'])
        _ = GradeLog.restore(data['gradelog'])
        _ = Profile.restore(data['profiles'])
        _ = Flashcard.restore(data['flashcards'])

    print("Data restored to the new database.")

@custom_cli.command('backup_data')
def backup_data():
    data = extract_data()
    save_data_to_json(data)
    backup_database(app.config['SQLALCHEMY_DATABASE_URI'], app.config['SQLALCHEMY_BACKUP_URI'])

@custom_cli.command('restore_data')
def restore_data_command():
    data = load_data_from_json()
    restore_data(data)

app.cli.add_command(custom_cli)

def list_all_flashcards():
    flashcards = Flashcard.query.all()
    if not flashcards:
        return "No flashcards found."
    return "\n".join([f"- {fc.read()['title']}: {fc.read()['content']}" for fc in flashcards])





def list_user_flashcards():
    user_id = g.current_user.id
    flashcards = Flashcard.query.filter_by(_user_id=user_id).all()
    if not flashcards:
        return "You don't have any flashcards yet."
    return "\n".join([f"- {fc.read()['title']}: {fc.read()['content']}" for fc in flashcards])

def list_all_user_products():
    user_id = g.current_user.id
    user_name = f"User #{user_id}"

    items = Flashcard.query.filter_by(_user_id=user_id).all()
    groups = Deck.query.filter_by(_user_id=user_id).all()

    response_lines = [f"{user_name}'s products are:\n"]

    if not items:
        response_lines.append("No items found.")
        return "\n".join(response_lines)

    for item in items:
        data = item.read()
        group = Deck.query.get(item._deck_id) if hasattr(item, '_deck_id') and item._deck_id else None
        group_name = group.title if group else "None"

        response_lines.append(f"Group name: {group_name}")
        response_lines.append(f"Item name: {data['title']}")
        response_lines.append("Number of items: 1")
        response_lines.append(f"Description: {data['content']}\n")

    return "\n".join(response_lines)


def get_item_group(item_title):
    item = Flashcard.query.filter_by(_title=item_title).first()
    if not item:
        return f"No item titled '{item_title}' found."

    group = Deck.query.get(item._deck_id) if item._deck_id else None
    if group:
        return f"The item '{item_title}' belongs to the group '{group.title}'."
    return f"The item '{item_title}' is not assigned to any group."


def handle_internal_intents(question: str):
    q = question.lower()

    # Keywords we'll match
    keywords_items = ["list", "show", "give", "state", "display"]
    products_alias = ["item", "product", "flashcard"]
    decks_alias = ["group", "deck"]

    # Check for variations
    if any(k in q for k in keywords_items) and any(p in q for p in products_alias + decks_alias):
        return list_all_user_products()

    if "2nd product" in q or "second product" in q:
        flashcards = Flashcard.query.filter_by(_user_id=g.current_user.id).all()
        if len(flashcards) >= 2:
            fc = flashcards[1].read()
            return f"Your second product is:\n- {fc['title']}: {fc['content']}"
        return "You don't have a second product."

    if "what item is this group in" in q:
        # Simulated interpretation - improve later with NLP
        return "Please specify which group (deck) you mean so I can tell you the items (flashcards) in it."

    return None


def get_flashcards_by_keyword(keyword):
    flashcards = Flashcard.query.filter(Flashcard._content.ilike(f"%{keyword}%")).all()
    if not flashcards:
        return f"No flashcards found for keyword '{keyword}'."
    return "\n".join([f"- {fc.read()['title']}: {fc.read()['content']}" for fc in flashcards])


def update_flashcard(title, new_content):
    flashcard = Flashcard.query.filter_by(_title=title).first()
    if not flashcard:
        return f"Flashcard titled '{title}' not found."
    flashcard._content = new_content
    db.session.commit()
    return f"Flashcard '{title}' updated successfully."


genai.configure(api_key="AIzaSyD7DQZlIvCo79fjHjUBYrApmFkRKZ12HSE")
model = genai.GenerativeModel('gemini-2.0-flash')
@app.route('/api/ai/help', methods=['POST'])
@token_required()
def ai_homework_help():
    data = request.get_json()
    question = data.get("question", "").lower()

    # Check for internal intents first
    response_text = handle_internal_intents(question)
    if response_text:
        new_entry = ChatLog(question=question, response=response_text)
        new_entry.create()
        return jsonify({"response": response_text}), 200

    if not question:
        return jsonify({"error": "No question provided."}), 400

    try:
        # Fetch user's flashcards and groups
        user_id = g.current_user.id
        flashcards = Flashcard.query.filter_by(_user_id=user_id).all()
        decks = Deck.query.filter_by(_user_id=user_id).all()

        # Prepare data string for the AI prompt
        flashcard_info = "\n".join([f"- {fc.read()['title']}: {fc.read()['content']}" for fc in flashcards]) or "No items."
        deck_info = "\n".join([f"- {deck.title}" for deck in decks]) or "No groups."

        # Inject data into AI prompt
        ai_prompt = (
            f"You are the Optivize Assistant, also known as OptiBot. The user has the following products:\n"
            f"Groups:\n{deck_info}\n\n"
            f"Items:\n{flashcard_info}\n\n"
            f"The user asks: {question}\n"
            f"Answer the question using the data above if it helps."
        )

        response = model.generate_content(ai_prompt)
        response_text = response.text

        # Save to chat log
        new_entry = ChatLog(question=question, response=response_text)
        new_entry.create()
        return jsonify({"response": response_text}), 200

    except Exception as e:
        print("error!", e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai/update', methods=['PUT'])
def update_ai_question():
    data = request.get_json()
    old_question = data.get("oldQuestion", "")
    new_question = data.get("newQuestion", "")
    if not old_question or not new_question:
        return jsonify({"error": "Both old and new questions are required."}), 400
    # Fetch the old log
    log = ChatLog.query.filter_by(_question=old_question).first()
    if not log:
        return jsonify({"error": "Old question not found."}), 404
    try:
        # Generate a new response for the new question
        response = model.generate_content(
            f"You are the Optivize Assitant, also known as OptiBot. Although you are helpful with everything, you are a customer service chatbot for a business. "
            f"Despite this, you can answer any question.\n"
            f"Here is your prompt: {new_question}"
        )
        new_response = response.text
        # Update the database entry
        log._question = new_question
        log._response = new_response
        db.session.commit()
        return jsonify({"response": new_response}), 200
    except Exception as e:
        print("Error during update:", e)
        return jsonify({"error": str(e)}), 500
@app.route('/api/ai/logs', methods=['GET'])
def fetch_all_logs():
    try:
        logs = ChatLog.query.all()
        return jsonify([log.read() for log in logs]), 200
    except Exception as e:
        print("Error fetching logs:", e)
        return jsonify({"error": str(e)}), 500
@app.route("/api/ai/delete", methods=["DELETE"])
def delete_ai_chat_logs():
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400
    if not data:
        return jsonify({"error": "No data provided."}), 400
    log = ChatLog.query.filter_by(_question=data.get("question", "")).first()
    if not log:
        return jsonify({"error": "Chat log not found."}), 404
    log.delete()
    return jsonify({"response": "Chat log deleted"}), 200
    


    
@app.route('/api/data')
def get_data():
    InfoDb = [
        {"FirstName": "Zafeer", "LastName": "Ahmed", "DOB": "January 11", "Residence": "San Diego", "Email": "zafeer10ahmed@gmail.com", "Owns_Cars": ["Tesla Model 3"]},
        {"FirstName": "Arush", "LastName": "Shah", "DOB": "December 20", "Residence": "San Diego", "Email": "emailarushshah@gmail.com", "Owns_Cars": ["Tesla Model 3"]},
        {"FirstName": "Nolan", "LastName": "Yu", "DOB": "October 7", "Residence": "San Diego", "Email": "nolanyu2@gmail.com", "Owns_Cars": ["Mazda"]},
        {"FirstName": "Xavier", "LastName": "Thompson", "DOB": "January 23", "Residence": "San Diego", "Email": "xavierathompson@gmail.com", "Favorite_Foods": "Popcorn"},
        {"FirstName": "Armaghan", "LastName": "Zarak", "DOB": "October 21", "Residence": "San Diego", "Email": "Armaghanz@icloud.com", "Owns_Vehicles": ["2015-scooter", "Half-a-bike", "2013-Honda-Pilot", "The-other-half-of-the-bike"]}
    ]
    return jsonify(InfoDb)

def init_database():
    try:
        with app.app_context():
            # Create all tables at once
            db.create_all()
            
            # Only initialize data if tables are empty
            if not User.query.first():
                initUsers()
                initProfiles()
                initGradeLog()
                initDecks()
                
            db.session.commit()
            print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {str(e)}")
        db.session.rollback()


if __name__ == "__main__":
    if os.environ.get('FLASK_ENV') == 'production':
        # Production settings
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/volumes/user_management.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    else:
        # Development settings
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/volumes/user_management.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        
    app.config['TIMEZONE'] = 'America/Los_Angeles'
    init_database()
    app.run(host="0.0.0.0", port="8212")






# Route to add a new leaderboard entry
@app.route('/api/leaderboard/apush/add', methods=['POST'])
def add_leaderboard_entry():
    try:
        data = request.get_json()
        name = data.get('name')
        score = data.get('score')

        if not name or score is None:
            return jsonify({'error': 'Name and score are required'}), 400

        # Add the new entry to the database
        new_entry = LeaderboardEntry(name=name, score=int(score))
        new_entry.create()
        return jsonify(new_entry.read()), 201  # Return the new entry
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route to delete a leaderboard entry
@app.route('/api/leaderboard/apush/delete', methods=['DELETE'])
def delete_leaderboard_entry():
    try:
        data = request.get_json()
        entry_id = data.get('id')

        if not entry_id:
            return jsonify({'error': 'ID is required'}), 400

        # Find and delete the entry
        entry = LeaderboardEntry.query.get(entry_id)
        if not entry:
            return jsonify({'error': 'Leaderboard entry not found'}), 404

        entry.delete()
        return jsonify({'message': f'Entry with ID {entry_id} has been deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
