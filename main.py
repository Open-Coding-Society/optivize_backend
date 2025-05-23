# Main.py, imports from flask
import json
from __init__ import app, db
import google.generativeai as genai
from __init__ import app, db
import requests
import json
import os
from sqlalchemy.orm import joinedload
from urllib.parse import urljoin, urlparse
from flask import abort, redirect, render_template, request, send_from_directory, url_for, jsonify
from flask_login import current_user, login_user, logout_user
from flask.cli import AppGroup
from flask_login import current_user, login_required
from flask import current_app
from flask import g
from api import gradelog
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
from api.zapier import zapier_api #import zapier_api



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
from api.studylog import product_api
from api.gradelog import gradelog_api
from api.profile import profile_api
from api.tips import tips_api
from api.leaderboard import leaderboard_api
from api.calendarv2 import calendar_api_v3
from api.google_api import google_api




# database Initialization functions
from model.user import User, initUsers
from model.section import Section, initSections
from model.group import Group, initGroups
from model.channel import Channel, initChannels
from model.post import Post, initPosts
from model.nestPost import NestPost, initNestPosts
from model.vote import Vote, initVotes
from model.flashcard import Flashcard, initFlashcards
from model.studylog import productSalesPrediction, initproductSalesPredictions
from model.gradelog import initGradeLog
from model.profiles import Profile, initProfiles
from model.chatlog import ChatLog, initChatLogs
from model.gradelog import GradeLog
from model.deck import Deck, initDecks
from model.calendar import Event, initEvents
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
app.register_blueprint(product_api)
app.register_blueprint(gradelog_api)
app.register_blueprint(profile_api)
app.register_blueprint(tips_api)
app.register_blueprint(deck_api)
app.register_blueprint(leaderboard_api)
app.register_blueprint(calendar_api_v3)
app.register_blueprint(zapier_api)
app.register_blueprint(google_api)





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

@app.before_request
def load_logged_in_user():
    g.current_user = current_user if current_user.is_authenticated else None


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
    productSalesPrediction()
    initproductSalesPredictions()
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
        data['studylogs'] = [log.read() for log in productSalesPrediction.query.all()]
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
        _ = productSalesPrediction.restore(data['studylogs'])
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

# Respond to "what can you do" or similar questions
def get_help_response(q):
    if any(phrase in q for phrase in ["what can you do", "help", "abilities", "capabilities", "how can you help", "commands"]):
        return (
            "Here's what I can help you with regarding inventory and flashcards:\n\n"
            "- **List Products**: View all your items and the groups they belong to.\n"
            "- **Get Product Info**: Ask about your 2nd product or any specific item.\n"
            "- **Create Item**: 'Add new item called [title] with content [content]'.\n"
            "- **Update Item**: 'Update item [title] with new content [content]'.\n"
            "- **Delete Item**: 'Delete item [title]'.\n"
            "- **Create Group**: 'Create group [title]'.\n"
            "- **Delete Group**: 'Delete group [title]'.\n"
            "- **Group Info**: Ask 'What group is [item] in?'\n\n"
            "You can also ask about flashcards, including ones you imported from Google Sheets!"
        )

 # Block prediction requests and redirect users
    if any(phrase in q for phrase in ["can you make predictions", "make prediction", "can you predict", "predict product", "predict success"]):
        return (
            "🚫 Sorry, I can’t make predictions here.\n\n"
            "👉 But you can visit the [Optivize Prediction Portal](https://zafeera123.github.io/optivize_frontend/navigation/log) to try it out!\n\n"
            "**Here’s how it works:**\n"
            "- Enter your product's type, price, marketing effort, and distribution.\n"
            "- Our AI model will give you a success score (0–100) along with business advice.\n"
            "- You’ll also get detailed insights on pricing, seasonality match, and marketing effectiveness.\n\n"
            "Let me know if you need help with inventory or flashcards!"
        )

def list_user_flashcards():
    user_id = g.current_user.id
    flashcards = Flashcard.query.filter_by(_user_id=user_id).all()
    if not flashcards:
        return "You don't have any flashcards yet."
    return "\n".join([f"- {fc.read()['title']}: {fc.read()['content']}" for fc in flashcards])


def list_all_user_products():
    user_id = g.current_user.id
    user = User.query.get(user_id)  # Corrected line
    user_name = user.name if user else f"User #{user_id}"

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


def create_flashcard(title, content, user_id, deck_title=None):
    deck = None
    if deck_title:
        deck = Deck.query.filter_by(_title=deck_title, _user_id=user_id).first()
        if not deck:
            deck = Deck(title=deck_title, user_id=user_id)
            deck.create()
    flashcard = Flashcard(title=title, content=content, user_id=user_id, deck_id=deck.id if deck else None)
    return flashcard.create()

def delete_flashcard(title, user_id):
    flashcard = Flashcard.query.filter_by(_title=title, _user_id=user_id).first()
    if flashcard:
        flashcard.delete()
        return f"Item '{title}' was deleted."
    return f"No item titled '{title}' found."

def create_group(title, user_id):
    deck = Deck.query.filter_by(_title=title, _user_id=user_id).first()
    if deck:
        return f"Group '{title}' already exists."
    new_deck = Deck(title=title, user_id=user_id)
    new_deck.create()
    return f"Group '{title}' was created."

def update_flashcard(title, new_content, user_id):
    flashcard = Flashcard.query.filter(
        Flashcard._user_id == user_id,
        db.func.lower(Flashcard._title) == title.lower()
    ).first()
    if not flashcard:
        return f"Flashcard titled '{title}' not found for your account."
    
    flashcard._content = new_content
    db.session.commit()
    return f"Flashcard '{flashcard._title}' was updated successfully."


def update_group(old_title, new_title, user_id):
    deck = Deck.query.filter(
        Deck._user_id == user_id,
        db.func.lower(Deck._title) == old_title.lower()
    ).first()
    if not deck:
        return f"Group titled '{old_title}' not found."

    deck.title = new_title  # uses the @title.setter property
    db.session.commit()
    return f"Group title updated from '{old_title}' to '{new_title}'."



def delete_group(title, user_id):
    deck = None

    # Step 1: Look through user's flashcards and safely join to deck objects
    user_flashcards = Flashcard.query.options(joinedload(Flashcard.deck)).filter_by(_user_id=user_id).all()

    for fc in user_flashcards:
        group = fc.deck  # This safely references the deck object if it exists
        if group and group.title.lower() == title.lower():
            deck = group
            break

    # Step 2: If no matching deck found, return
    if not deck:
        return f"Group '{title}' not found."

    # Step 3: Unassign user's flashcards from this group
    Flashcard.query.filter_by(_user_id=user_id, _deck_id=deck.id).update({'_deck_id': None})

    # Step 4: Check if other users still use this deck
    others_use_it = Flashcard.query.filter(
        Flashcard._deck_id == deck.id,
        Flashcard._user_id != user_id
    ).count() > 0

    # Step 5: Delete deck only if no one else is using it
    if not others_use_it:
        db.session.delete(deck)

    db.session.commit()
    return f"Group '{title}' was deleted or unassigned from your items."




pending_intents = {}  # temp dictionary: user_id -> {'action': ..., 'title': ..., ...}

def handle_internal_intents(question: str):
    q = question.lower()
    user_id = g.current_user.id
        


    if "predict product" in q or "product prediction" in q:
        return "I cannot make product predictions here. I can only work with the inventory database. However, to get a product success prediction, provide: product type, seasonality, price, marketing score (1–10), and number of distribution channels."
    elif "train product model" in q:
        return "How it works is to train the product model, send a POST request to `/api/train` with at least 5 labeled product samples."
    elif "product categories" in q:
        return "product categories include: chocolate, fruit, nut, seasonal, and premium. These affect pricing and seasonality."


    # Shortcut: "add item [title] to group [group]"
    if "add item" in q and "to group" in q:
        try:
            title = q.split("add item")[1].split("to group")[0].strip()
            group_title = q.split("to group")[1].strip()
            content = "(no content)"  # default content

            create_flashcard(title=title, content=content, user_id=user_id, deck_title=group_title)
            return f"Okay, I've added '{title}' to the '{group_title}' group."
        except Exception as e:
            print("Add item to group failed:", e)
            return "Sorry, I couldn’t parse that. Try: 'add item apple to group snacks'"

    
    # Step 1: Handle follow-ups for staged actions
    if user_id in pending_intents:
        intent = pending_intents[user_id]

        # Follow-up: Create item with group
        if intent['action'] == 'create_item_waiting_for_group':
            group_title = q.strip()
            create_flashcard(
                title=intent['title'],
                content=intent['content'],
                user_id=user_id,
                deck_title=group_title
            )
            del pending_intents[user_id]
            return f"Item '{intent['title']}' was created and added to group '{group_title}'."

        # Follow-up: Confirm delete
        if intent['action'] == 'confirm_delete':
            confirmed = q.strip().lower() in ["yes", "confirm", "delete"]
            if confirmed:
                delete_flashcard(intent['title'], user_id)
                del pending_intents[user_id]
                return f"Item '{intent['title']}' has been deleted."
            else:
                del pending_intents[user_id]
                return "Okay, deletion canceled."

    # Step 2: Main command parsing

    # Create item with follow-up for group
    if "add new item" in q or "create item" in q:
        try:
            parts = q.split("called")[1].split("with content")
            title = parts[0].strip()
            content = parts[1].strip()

            pending_intents[user_id] = {
                "action": "create_item_waiting_for_group",
                "title": title,
                "content": content
            }
            return f"What group would you like to add the item '{title}' to?"
        except Exception:
            return "Sorry, I couldn’t parse the item creation request."
    
    import re

    if "update group" in q and "to" in q:
        match = re.search(r"update group (.+?) to (.+)", q, re.IGNORECASE)
        if match:
            old_title = match.group(1).strip()
            new_title = match.group(2).strip()
            return update_group(old_title, new_title, user_id)
        else:
            return "Sorry, I couldn’t update the group title. Try saying: 'update group OldName to NewName'."


    import re

    if "update item" in q:
        try:
            # Use regex to robustly extract title and new content
            match = re.search(r"update item (.+?) with new content (.+)", question, re.IGNORECASE)
            if not match:
                return "Sorry, I couldn’t parse the item update. Please use: 'update item [title] with new content [content]'"

            title = match.group(1).strip()
            new_content = match.group(2).strip()

            flashcard = Flashcard.query.filter_by(_title=title, _user_id=user_id).first()
            if not flashcard:
                return f"No item titled '{title}' found."

            group = Deck.query.get(flashcard._deck_id) if flashcard._deck_id else None
            group_name = group.title if group else "None"

            update_flashcard(title, new_content, user_id)
            return f"Item '{title}' was updated successfully (previously in group '{group_name}')."

        except Exception as e:
            print("Update item error:", e)
            return "Something went wrong while updating the item."



    # Delete item with confirmation
    if "delete item" in q:
        try:
            title = q.split("delete item")[-1].strip()
            flashcard = Flashcard.query.filter_by(_title=title, _user_id=user_id).first()
            if not flashcard:
                return f"No item titled '{title}' found."

            group = Deck.query.get(flashcard._deck_id) if flashcard._deck_id else None
            group_name = group.title if group else "None"

            pending_intents[user_id] = {
                "action": "confirm_delete",
                "title": title
            }
            return f"Item '{title}' is in group '{group_name}'. Do you want to delete it? (yes/no)"
        except Exception:
            return "Sorry, I couldn’t process your delete request."

    # Create group
    if "create group" in q or "add group" in q:
        try:
            title = q.split("group")[-1].strip()
            return create_group(title, user_id)
        except Exception:
            return "Sorry, couldn’t create the group."

    # Delete group
    if "delete group" in q:
        try:
            title = q.split("delete group")[-1].strip()
            return delete_group(title, user_id)
        except Exception:
            return "Sorry, couldn’t delete the group."

    # Get group of item
    if "what group is" in q and "in" in q:
        item_title = q.split("group is")[-1].replace("in", "").strip()
        return get_item_group(item_title)

    # List items and groups
    if any(k in q for k in ["list", "show", "give", "state", "display"]) and any(p in q for p in ["item", "product", "flashcard", "deck", "group"]):
        return list_all_user_products()

    # Get second item
    if "2nd product" in q or "second product" in q:
        flashcards = Flashcard.query.filter_by(_user_id=user_id).all()
        if len(flashcards) >= 2:
            fc = flashcards[1].read()
            return f"Your second product is:\n- {fc['title']}: {fc['content']}"
        return "You don't have a second product."

    return None


def get_flashcards_by_keyword(keyword):
    flashcards = Flashcard.query.filter(Flashcard._content.ilike(f"%{keyword}%")).all()
    if not flashcards:
        return f"No flashcards found for keyword '{keyword}'."
    return "\n".join([f"- {fc.read()['title']}: {fc.read()['content']}" for fc in flashcards])


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
            f"You are OptiBot, a customer service and product intelligence assistant.\n\n"
            f"Here’s what you should know about the user's product tools:\n"
            f"- They manage flashcards and groups (like decks).\n"
            f"- They also use a **product Sales Prediction API**, which:\n"
            f"    • Uses features like product type, seasonality, price, marketing score, and distribution reach.\n"
            f"    • Predicts success likelihood using a trained Random Forest model.\n"
            f"    • Assigns scores and gives insights on pricing, seasonality, and marketing effectiveness.\n"
            f"    • Provides advice like 'Reformulate product concept' or 'Increase marketing budget'.\n\n"
            f"User’s decks:\n{deck_info}\n\n"
            f"User’s items:\n{flashcard_info}\n\n"
            f"User asks: {question}\n"
            f"Respond clearly. If it’s about product prediction, use the rules and features described above."
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
                initproductSalesPredictions()
                
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

