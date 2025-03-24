from flask import request
from flask import current_app, g
from functools import wraps
import jwt
from model.user import User

def token_required(roles=None):
    def decorator(func_to_guard):
        @wraps(func_to_guard)
        def decorated(*args, **kwargs):
            # Check for the token in cookies
            token = request.cookies.get(current_app.config["JWT_TOKEN_NAME"])
            if not token:
                print("Token is missing")  # Debugging log
                return {
                    "message": "Token is missing",
                    "error": "Unauthorized"
                }, 401

            try:
                # Decode the token
                data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
                print(f"Decoded Token: {data}")  # Debugging log

                # Find the user in the database
                current_user = User.query.filter_by(_uid=data["_uid"]).first()
                if not current_user:
                    print("User not found in database")  # Debugging log
                    return {
                        "message": "User not found",
                        "error": "Unauthorized",
                        "data": data
                    }, 401

                # Check roles if specified
                if roles and current_user.role not in roles:
                    print(f"User does not have required role: {current_user.role}")  # Debugging log
                    return {
                        "message": "User does not have the required role",
                        "error": "Forbidden",
                        "data": data
                    }, 403

                # Set the authenticated user
                g.current_user = current_user
                print(f"Authenticated User: {current_user._uid}, Role: {current_user.role}")  # Debugging log
            except jwt.ExpiredSignatureError:
                print("Token has expired")  # Debugging log
                return {
                    "message": "Token has expired",
                    "error": "Unauthorized"
                }, 401
            except jwt.InvalidTokenError:
                print("Invalid token")  # Debugging log
                return {
                    "message": "Invalid token",
                    "error": "Unauthorized"
                }, 401
            except Exception as e:
                print(f"Unexpected error: {e}")  # Debugging log
                return {
                    "message": "An error occurred",
                    "error": str(e)
                }, 500

            # Call the protected function
            return func_to_guard(*args, **kwargs)
        return decorated
    return decorator
