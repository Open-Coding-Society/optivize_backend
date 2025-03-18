from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError
from __init__ import db
from model.profiles import Profile

# Blueprint setup
profile_api = Blueprint('profile_api', __name__, url_prefix='/api')
api = Api(profile_api)

# ProfileAPI class to handle CRUD operations
class ProfileAPI:
    class CRUD(Resource):
        def get(self):
            try:
                # Retrieve all profiles from the database
                profiles = Profile.query.all()
                return jsonify([profile.read() for profile in profiles])
            except Exception as e:
                return {'message': f"An error occurred: {str(e)}"}, 500

        def post(self):
            try:
                data = request.get_json()

                # Validate input data
                if not data:
                    return {'message': 'No input data provided'}, 400

                name = data.get('name')
                classes = data.get('classes')
                favorite_class = data.get('favorite_class')
                grade = data.get('grade')

                if not name or not favorite_class or not grade:
                    return {'message': 'Missing required fields'}, 400

                # Create and save the new profile
                profile = Profile(name=name, classes=classes, favorite_class=favorite_class, grade=grade)
                profile.create()

                return jsonify(profile.read()), 201
            except IntegrityError:
                db.session.rollback()
                return {'message': 'Profile with the same name already exists'}, 400
            except Exception as e:
                db.session.rollback()
                return {'message': f"An unexpected error occurred: {str(e)}"}, 500

        def put(self):
            try:
                data = request.get_json()

                # Validate input data
                if not data or 'id' not in data:
                    return {'message': 'No input data provided or missing ID'}, 400

                profile = Profile.query.get(data['id'])

                if not profile:
                    return {'message': 'Profile not found'}, 404

                # Update the profile
                profile.update(data)

                return jsonify(profile.read())
            except Exception as e:
                return {'message': f"An error occurred: {str(e)}"}, 500

        def delete(self):
            try:
                data = request.get_json()

                # Validate input data
                if not data or 'id' not in data:
                    return {'message': 'No input data provided or missing ID'}, 400

                profile = Profile.query.get(data['id'])

                if not profile:
                    return {'message': 'Profile not found'}, 404

                # Delete the profile
                profile.delete()

                return {'message': 'Profile deleted successfully'}, 200
            except Exception as e:
                return {'message': f"An error occurred: {str(e)}"}, 500
                
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

    api.add_resource(CRUD, '/profiles')

# Example usage with Postman:
# GET /api/profiles - Retrieve all profiles
# POST /api/profiles - Add a new profile with JSON body
# PUT /api/profiles - Update an existing profile with JSON body (must include 'id')
# DELETE /api/profiles - Delete a profile with JSON body (must include 'id')
