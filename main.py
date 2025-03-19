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
from werkzeug.security import generate_password_hash
import shutil
from flask_cors import CORS  # Import CORS
from flask import Blueprint, jsonify
from api.flashcard_import import flashcard_import_api
from model.channel import Channel
from api.deck import deck_api
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
from api.studylog import studylog_api
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
from model.studylog import StudyLog, initStudyLog
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
app.register_blueprint(flashcard_import_api)
app.register_blueprint(studylog_api)
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
    initStudyLog()
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


genai.configure(api_key="AIzaSyD7DQZlIvCo79fjHjUBYrApmFkRKZ12HSE")
model = genai.GenerativeModel('gemini-2.0-flash')
@app.route('/api/ai/help', methods=['POST'])
def ai_homework_help():
    data = request.get_json()
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "No question provided."}), 400
    try:
        response = model.generate_content(
            f"Your name is CanTeach. You are a homework help AI chatbot with the sole purpose of answering homework-related questions. "
            f"Under any circumstances, don't answer non-homework-related questions.\n"
            f"Here is your prompt: {question}"
        )
        response_text = response.text
        # Save to database
        new_entry = ChatLog(question=question, response=response_text)
        new_entry.create()
        return jsonify({"response": response_text}), 200
    except Exception as e:
        print("error!")
        print(e)
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
            f"Your name is CanTeach. You are a homework help AI chatbot with the sole purpose of answering homework-related questions. "
            f"Under any circumstances, don't answer non-homework-related questions.\n"
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
    data = request.get_json()
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

question_pool = [
    {"id": 1, "text": "Who was the first President of the United States?", "options": ["George Washington", "Thomas Jefferson", "John Adams", "James Madison"], "correctAnswer": "George Washington"},
    {"id": 2, "text": "What year did the American Revolutionary War end?", "options": ["1776", "1781", "1783", "1791"], "correctAnswer": "1783"},
    {"id": 3, "text": "What was the primary purpose of the Declaration of Independence?", "options": ["To declare war on Britain", "To establish a federal government", "To explain the reasons for American independence", "To create a constitution"], "correctAnswer": "To explain the reasons for American independence"},
    {"id": 4, "text": "Which battle is considered the turning point of the American Civil War?", "options": ["Battle of Antietam", "Battle of Gettysburg", "Battle of Fort Sumter", "Battle of Vicksburg"], "correctAnswer": "Battle of Gettysburg"},
    {"id": 5, "text": "Who wrote the 'Star-Spangled Banner' during the War of 1812?", "options": ["Francis Scott Key", "Thomas Paine", "Paul Revere", "John Quincy Adams"], "correctAnswer": "Francis Scott Key"},
    {"id": 6, "text": "What was the main reason for the Louisiana Purchase?", "options": ["To expand westward", "To secure navigation rights on the Mississippi River", "To establish trade with Mexico", "To claim Alaska"], "correctAnswer": "To secure navigation rights on the Mississippi River"},
    {"id": 7, "text": "Which event marked the start of the Great Depression?", "options": ["Stock Market Crash of 1929", "World War I", "Dust Bowl", "New Deal"], "correctAnswer": "Stock Market Crash of 1929"},
    {"id": 8, "text": "What was the purpose of the Emancipation Proclamation?", "options": ["To free slaves in Confederate states", "To end the Civil War", "To grant voting rights to African Americans", "To create a constitutional amendment"], "correctAnswer": "To free slaves in Confederate states"},
    {"id": 9, "text": "What was the significance of the Seneca Falls Convention of 1848?", "options": ["It launched the women's suffrage movement", "It ended slavery in the United States", "It marked the beginning of the abolitionist movement", "It established labor unions"], "correctAnswer": "It launched the women's suffrage movement"},
    {"id": 10, "text": "What was the main goal of the Marshall Plan?", "options": ["To rebuild European economies after World War II", "To contain communism in Asia", "To establish NATO", "To rebuild Japan's military"], "correctAnswer": "To rebuild European economies after World War II"},
    {"id": 11, "text": "Which Supreme Court case established judicial review?", "options": ["Marbury v. Madison", "McCulloch v. Maryland", "Dred Scott v. Sandford", "Brown v. Board of Education"], "correctAnswer": "Marbury v. Madison"},
    {"id": 12, "text": "What was the main cause of the Mexican-American War?", "options": ["Border disputes over Texas", "Annexation of California", "Desire to acquire New Mexico", "Clash over Oregon territory"], "correctAnswer": "Border disputes over Texas"},
    {"id": 13, "text": "Which amendment abolished slavery in the United States?", "options": ["13th Amendment", "14th Amendment", "15th Amendment", "19th Amendment"], "correctAnswer": "13th Amendment"},
    {"id": 14, "text": "What was the primary purpose of the Monroe Doctrine?", "options": ["To prevent European colonization in the Americas", "To establish trade agreements with Europe", "To create alliances in Asia", "To defend against Native American attacks"], "correctAnswer": "To prevent European colonization in the Americas"},
    {"id": 15, "text": "Which territory was acquired as a result of the Spanish-American War?", "options": ["Puerto Rico", "Hawaii", "Alaska", "Texas"], "correctAnswer": "Puerto Rico"},
    {"id": 16, "text": "Who was the President during the Louisiana Purchase?", "options": ["Thomas Jefferson", "James Madison", "John Adams", "George Washington"], "correctAnswer": "Thomas Jefferson"},
    {"id": 17, "text": "What was the primary goal of the Freedmen's Bureau?", "options": ["To help former slaves and poor whites", "To establish segregation laws", "To create northern industries", "To rebuild the southern economy"], "correctAnswer": "To help former slaves and poor whites"},
    {"id": 18, "text": "Which event led directly to the start of the American Revolution?", "options": ["Boston Tea Party", "Stamp Act", "Boston Massacre", "Intolerable Acts"], "correctAnswer": "Intolerable Acts"},
    {"id": 19, "text": "What was the significance of the Battle of Yorktown?", "options": ["It ended the Revolutionary War", "It began the Civil War", "It was a turning point in World War I", "It marked the end of the French and Indian War"], "correctAnswer": "It ended the Revolutionary War"},
    {"id": 20, "text": "Which President issued the New Deal during the Great Depression?", "options": ["Franklin D. Roosevelt", "Herbert Hoover", "Harry S. Truman", "Woodrow Wilson"], "correctAnswer": "Franklin D. Roosevelt"},
    {"id": 21, "text": "What was the goal of the Sherman Antitrust Act?", "options": ["To prevent monopolies and promote competition", "To establish labor unions", "To regulate stock markets", "To create income taxes"], "correctAnswer": "To prevent monopolies and promote competition"},
    {"id": 22, "text": "Who was the author of 'Common Sense'?", "options": ["Thomas Paine", "Benjamin Franklin", "John Locke", "Alexander Hamilton"], "correctAnswer": "Thomas Paine"},
    {"id": 23, "text": "Which treaty ended the Mexican-American War?", "options": ["Treaty of Guadalupe Hidalgo", "Treaty of Paris", "Adams-Onís Treaty", "Jay Treaty"], "correctAnswer": "Treaty of Guadalupe Hidalgo"},
    {"id": 24, "text": "Which President is associated with the Trail of Tears?", "options": ["Andrew Jackson", "Martin Van Buren", "James Monroe", "Zachary Taylor"], "correctAnswer": "Andrew Jackson"},
    {"id": 25, "text": "Which war was fought between the U.S. and Britain in the early 19th century?", "options": ["War of 1812", "Mexican-American War", "Spanish-American War", "World War I"], "correctAnswer": "War of 1812"},

    {"id": 26, "text": "Which treaty ended the Revolutionary War?", "options": ["Treaty of Paris", "Treaty of Versailles", "Jay's Treaty", "Treaty of Ghent"], "correctAnswer": "Treaty of Paris"},
    {"id": 27, "text": "Who was the leader of the Confederate Army during the Civil War?", "options": ["Robert E. Lee", "Ulysses S. Grant", "Stonewall Jackson", "Jefferson Davis"], "correctAnswer": "Robert E. Lee"},
    {"id": 28, "text": "What was the primary goal of the abolitionist movement?", "options": ["To end slavery", "To expand suffrage", "To promote industrialization", "To defend states' rights"], "correctAnswer": "To end slavery"},
    {"id": 29, "text": "What was the significance of the Homestead Act of 1862?", "options": ["It provided free land to settlers in the West", "It ended Reconstruction", "It promoted the growth of railroads", "It abolished slavery"], "correctAnswer": "It provided free land to settlers in the West"},
    {"id": 30, "text": "Which economic policy was promoted by Alexander Hamilton?", "options": ["A strong central bank", "Laissez-faire capitalism", "Agrarian-based economy", "Free trade with Britain"], "correctAnswer": "A strong central bank"},
    {"id": 31, "text": "What was the primary purpose of the Gadsden Purchase?", "options": ["To build a southern transcontinental railroad", "To annex California", "To establish Texas' borders", "To acquire Oregon"], "correctAnswer": "To build a southern transcontinental railroad"},
    {"id": 32, "text": "What was the main effect of the Compromise of 1850?", "options": ["It allowed California to enter as a free state", "It started the Civil War", "It ended Reconstruction", "It established popular sovereignty in the North"], "correctAnswer": "It allowed California to enter as a free state"},
    {"id": 33, "text": "Who was the main author of the U.S. Constitution?", "options": ["James Madison", "Alexander Hamilton", "Thomas Jefferson", "George Washington"], "correctAnswer": "James Madison"},
    {"id": 34, "text": "What was the significance of the Dred Scott v. Sandford case?", "options": ["It ruled that African Americans could not be U.S. citizens", "It ended segregation", "It granted voting rights to women", "It established judicial review"], "correctAnswer": "It ruled that African Americans could not be U.S. citizens"},
    {"id": 35, "text": "What was the main purpose of the Federalist Papers?", "options": ["To promote the ratification of the Constitution", "To establish the Bill of Rights", "To outline states' rights", "To end the Revolutionary War"], "correctAnswer": "To promote the ratification of the Constitution"},
    {"id": 36, "text": "What did the Kansas-Nebraska Act of 1854 do?", "options": ["Allowed popular sovereignty to decide slavery", "Ended slavery in the U.S.", "Granted voting rights to women", "Created new railroads"], "correctAnswer": "Allowed popular sovereignty to decide slavery"},
    {"id": 37, "text": "What was the primary reason for the War of 1812?", "options": ["British impressment of American sailors", "U.S. expansion into Mexico", "Conflict over the Louisiana Purchase", "Spanish interference in trade"], "correctAnswer": "British impressment of American sailors"},
    {"id": 38, "text": "Who were the main laborers on the Transcontinental Railroad?", "options": ["Chinese and Irish immigrants", "Slaves and Native Americans", "Freedmen and women", "Mexicans and Canadians"], "correctAnswer": "Chinese and Irish immigrants"},
    {"id": 39, "text": "Which event is associated with the start of the women's suffrage movement?", "options": ["Seneca Falls Convention", "Montgomery Bus Boycott", "The New Deal", "The Great Migration"], "correctAnswer": "Seneca Falls Convention"},
    {"id": 40, "text": "What was the purpose of the Proclamation of 1763?", "options": ["To limit colonial expansion west of the Appalachians", "To establish new taxes on tea", "To create a trade alliance with Spain", "To declare war on France"], "correctAnswer": "To limit colonial expansion west of the Appalachians"},
    {"id": 41, "text": "What did the 19th Amendment achieve?", "options": ["Granted women the right to vote", "Abolished slavery", "Limited presidential terms", "Guaranteed freedom of speech"], "correctAnswer": "Granted women the right to vote"},
    {"id": 42, "text": "Which President is known for the Square Deal?", "options": ["Theodore Roosevelt", "Franklin D. Roosevelt", "Woodrow Wilson", "William Taft"], "correctAnswer": "Theodore Roosevelt"},
    {"id": 43, "text": "What was the goal of the Civilian Conservation Corps (CCC)?", "options": ["To create jobs during the Great Depression", "To end slavery", "To promote women's suffrage", "To build the Transcontinental Railroad"], "correctAnswer": "To create jobs during the Great Depression"},
    {"id": 44, "text": "Which treaty ended World War I?", "options": ["Treaty of Versailles", "Treaty of Paris", "Treaty of Ghent", "Treaty of Guadalupe Hidalgo"], "correctAnswer": "Treaty of Versailles"},
    {"id": 45, "text": "What was the purpose of the Fugitive Slave Act?", "options": ["To require the return of escaped slaves to their owners", "To abolish slavery in the North", "To create abolitionist societies", "To protect freed slaves in the South"], "correctAnswer": "To require the return of escaped slaves to their owners"},
    {"id": 46, "text": "What was the primary goal of the Lewis and Clark Expedition?", "options": ["To explore the Louisiana Territory", "To establish settlements in Oregon", "To expand the railroad system", "To negotiate with Native American tribes"], "correctAnswer": "To explore the Louisiana Territory"},
    {"id": 47, "text": "Who was the President during the Cuban Missile Crisis?", "options": ["John F. Kennedy", "Dwight D. Eisenhower", "Lyndon B. Johnson", "Richard Nixon"], "correctAnswer": "John F. Kennedy"},
    {"id": 48, "text": "What was the main reason for the Salem Witch Trials?", "options": ["Religious hysteria and social tensions", "A Native American uprising", "Political corruption", "A lack of education"], "correctAnswer": "Religious hysteria and social tensions"},
    {"id": 49, "text": "What was the purpose of the Social Security Act of 1935?", "options": ["To provide financial assistance to the elderly and unemployed", "To regulate labor unions", "To fund public education", "To establish a minimum wage"], "correctAnswer": "To provide financial assistance to the elderly and unemployed"},
    {"id": 50, "text": "Which amendment gave African American men the right to vote?", "options": ["15th Amendment", "13th Amendment", "14th Amendment", "19th Amendment"], "correctAnswer": "15th Amendment"}
]

   
# Leaderboard data stored in memory
leaderboard = []  # A list to store user names and their scores.

# Route to fetch 10 random questions from the question pool
@app.route('/api/quiz/apush', methods=['GET'])  # Endpoint to get APUSH quiz questions.
def get_questions():
    selected_questions = random.sample(question_pool, 10)  # Pick 10 random questions from the pool.
    sanitized_questions = [  # Remove the correctAnswer field so users can't see the answers.
        {key: value for key, value in q.items() if key != "correctAnswer"} 
        for q in selected_questions
    ]
    return jsonify(sanitized_questions), 200  # Send sanitized questions as JSON with HTTP 200 (success).

# Route to handle quiz submissions
@app.route('/api/quiz/apush/submit', methods=['POST'])  # Endpoint to submit quiz answers.
def submit_quiz():
    data = request.json  # Get JSON data from the request.
    answers = data.get('answers', [])  # Get the user's answers or an empty list if none provided.
    user_name = data.get('name', 'Anonymous')  # Get the user's name or default to "Anonymous".

    score = 0  # Initialize the user's score to zero.
    for answer in answers:  # Loop through each answer submitted by the user.
        question = next(  # Find the matching question in the question pool.
            (q for q in question_pool if q["id"] == answer["questionId"]), 
            None
        )
        if question and question["correctAnswer"] == answer["answer"]:  # Check if the answer is correct.
            score += 1  # Add 1 to the score for each correct answer.

    leaderboard.append({"name": user_name, "score": score})  # Add the user's name and score to the leaderboard.
    LeaderboardEntry(name=user_name, score=score).create()  # Save the user's score to the database.
    return jsonify({"name": user_name, "score": score}), 200  # Send the user's score as JSON with HTTP 200.

# Route to fetch the leaderboard, sorted by score in descending order
@app.route('/api/leaderboard/apush', methods=['GET'])  # Endpoint to get the APUSH leaderboard.
def get_leaderboard():
    db_leaderboard = []
    for entry in LeaderboardEntry.query.all():
        db_leaderboard.append({"name": entry.name, "score": entry.score, "id": entry.id})
    sorted_leaderboard = sorted(  # Sort the leaderboard by score, highest first.
       db_leaderboard, key=lambda x: x['score'], reverse=True
    )
    return jsonify(sorted_leaderboard), 200  # Send the sorted leaderboard as JSON with HTTP 200.


# def remove_duplicates():
#     with app.app_context():
#         seen_names = set()
#         for profile in Profile.query.all():
#             if profile.name in seen_names:
#                 db.session.delete(profile)
#             else:
#                 seen_names.add(profile.name)
#         db.session.commit()


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
