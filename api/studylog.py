import jwt
from flask import Blueprint, request, jsonify, current_app, Response, g
from flask_restful import Api, Resource
from datetime import datetime
from __init__ import app, db
from api.jwt_authorize import token_required
from model.studylog import StudyLog
import json

# Create a Blueprint named 'studylog_api' with prefix '/api' for organizing routes related to StudyLog
studylog_api = Blueprint('studylog_api', __name__, url_prefix='/api')

# Create a Flask-RESTful API object from the blueprint
api = Api(studylog_api)

class StudyLogAPI:
    """
    This class encapsulates CRUD operations for the StudyLog model.
    Each method inside the CRUD resource class handles one of the 
    CRUD (Create, Read, Update, Delete) functionalities via HTTP methods.
    """
    class CRUD(Resource):

        # GET: Read all study logs from the database
        @token_required()
        def get(self):
            # Query all StudyLog records from database
            all_studylogs = StudyLog.query.all()

            # Prepare a list to hold each study log's data
            studylogs = []
            for log in all_studylogs:
                # Convert the study log object into a dictionary
                studylogs.append(log.read())

            # Return all study logs as JSON
            return jsonify(studylogs)

        # POST: Create a new study log
        @token_required()
        def post(self):
            try:
                # Parse the JSON body of the request
                data = request.get_json()
                
                # If there's no data in the request, return an error
                if not data:
                    return {'message': 'No input data provided'}, 400
                
                # Extract fields from the JSON body
                user_id = data.get('user_id')
                subject = data.get('subject')
                hours_studied = data.get('hours_studied')
                notes = data.get('notes')

                '''
                Example payload:
                {
                    "user_id": 1,
                    "subject": "AP Physics",
                    "hours_studied": 2.5,
                    "notes": "Studied Newton's Laws of Motion."
                }
                '''

                # Basic validation checks for required fields
                if not user_id:
                    return {'message': 'User ID is required'}, 400
                if not subject:
                    return {'message': 'Subject is required'}, 400
                if not hours_studied:
                    return {'message': 'Hours studied is required'}, 400
                if not notes:
                    return {'message': 'Notes is required'}, 400
                
                # Create a new StudyLog object
                studylog = StudyLog(user_id, subject, hours_studied, notes)
                
                # Print JSON data to console (debug logging)
                print(json.dumps({
                    "user_id": user_id,
                    "subject": subject,
                    "hours_studied": hours_studied,
                    "notes": notes
                }))
                
                # Save the new record to the database
                studylog.create()

                # Return the newly created study log as JSON
                return jsonify(studylog.read())
            
            except Exception as e:
                # If anything goes wrong, return an error message
                return {'message': f"An error occurred: {str(e)}"}, 500

        # PUT: Update an existing study log
        @token_required()
        def put(self):
            try:
                # Parse the JSON body of the request
                data = request.get_json()
                # If there's no data, return an error
                if not data:
                    return {'message': 'No input data provided'}, 400

                # Retrieve the ID of the log to be updated
                studylog_id = data.get('id')
                # Query for the specific StudyLog using the ID
                studylog = StudyLog.query.get(studylog_id)

                # If the record doesn't exist, return a 404
                if not studylog:
                    return {'message': 'StudyLog not found'}, 404

                # Update fields only if they are provided, otherwise keep existing values
                studylog.user_id = data.get('user_id', studylog.user_id)
                studylog.subject = data.get('subject', studylog.subject)
                studylog.hours_studied = data.get('hours_studied', studylog.hours_studied)
                studylog.notes = data.get('notes', studylog.notes)

                # Commit the changes to the database
                db.session.commit()

                return {'message': 'StudyLog updated successfully'}, 200

            except Exception as e:
                db.session.rollback()
                return {'message': f"An error occurred: {str(e)}"}, 500

        # DELETE: Remove an existing study log from the database
        @token_required()
        def delete(self):
            try:
                # Parse the JSON body of the request
                data = request.get_json()
                # If there's no data, return an error
                if not data:
                    return {'message': 'No input data provided'}, 400

                # Retrieve the ID of the log to be deleted
                studylog_id = data.get('id')
                # Find the corresponding StudyLog in the database
                studylog = StudyLog.query.get(studylog_id)

                # If no study log is found, return a 404
                if not studylog:
                    return {'message': 'StudyLog not found'}, 404

                # Delete the record
                db.session.delete(studylog)
                db.session.commit()

                # Return success message
                return {'message': 'StudyLog deleted successfully'}, 200
            
            except Exception as e:
                # Catch any errors and return a corresponding message
                return {'message': f"An error occurred: {str(e)}"}, 500

        @staticmethod
        def restore(data):
            """
            This static method helps in restoring multiple logs from a data source (e.g., JSON backup).
            It iterates through each record, removes the 'id' key to avoid conflicts, 
            then either updates or creates a new StudyLog in the database.
            """
            for log_data in data:
                # Remove 'id' since a new ID will be auto-generated in the DB
                _ = log_data.pop('id', None)
            
            # Retrieve user_id and subject from the data
            user_id = log_data.get("user_id", None)
            subject = log_data.get("subject", None)

            # Find an existing StudyLog record with matching user_id and subject
            studylog = StudyLog.query.filter_by(user_id=user_id, subject=subject).first()
            
            # If found, update it; otherwise create a new record
            if studylog:
                studylog.update(log_data)
            else:
                studylog = StudyLog(**log_data)
                studylog.create()
            
            # Commit the changes after each entry is processed
            db.session.commit()

    # Add the CRUD resource to the API, mapping to the '/studylognew' endpoint
    api.add_resource(CRUD, '/studylognew')