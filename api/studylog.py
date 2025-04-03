import logging
from pandas import DataFrame
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from model.studylog import CookieSalesPrediction

cookie_api = Blueprint('cookie_api', __name__, url_prefix='/api')
api = Api(cookie_api)

# ✅ Enable CORS with credentials support
CORS(cookie_api, resources={r"/*": {"origins": ["http://127.0.0.1:4887", "https://zafeera123.github.io"]}},
     supports_credentials=True)

# Load Model
try:
    model = joblib.load("titanic_cookie_model.pkl")
except FileNotFoundError:
    model = None  # No pre-trained model found
class CookiePredictionAPI(Resource):
    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def post(self):
        """Predict cookie success using a machine learning model."""
        logging.debug("Received POST request to /api/predict")

        data = request.get_json()
        logging.debug(f"Received Data: {data}")

        # Required fields from frontend
        required_fields = ['cookie_flavor', 'price', 'marketing']
        if not all(field in data for field in required_fields):
            return {'message': 'Missing required fields'}, 400

        if not model:
            return {'message': 'Model not trained. Please train the model first.'}, 500

        # Convert inputs into an array for model prediction
        input_data = np.array([[
            hash(data['cookie_flavor']) % 1000,  # Hashing flavor to numerical value
            data['price'],
            data['marketing']
        ]])

        # Predict success (returns probability between 0 and 1)
        success_probability = model.predict_proba(input_data)[0][1] * 100  # Convert to percentage

        logging.debug(f"Predicted Success Probability: {success_probability:.2f}%")

        return jsonify({'success_probability': round(success_probability, 2)})

class CookieTrainingAPI(Resource):
    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def post(self):
        """Train a new cookie prediction model, adding sample data if needed."""

        # Fetch existing data from the database
        predictions = CookieSalesPrediction.query.all()

        # If not enough data, insert sample data
        if len(predictions) < 10:
            crumbl_sample_data = [
                {"cookie_flavor": "Milk Chocolate Chip", "seasonality": "All Year", "price": 4.00, "marketing": 9, "customer_sentiment": 9, "predicted_success": 1},
                {"cookie_flavor": "Classic Pink Sugar", "seasonality": "All Year", "price": 3.75, "marketing": 8, "customer_sentiment": 8, "predicted_success": 1},
                {"cookie_flavor": "Cookies & Cream", "seasonality": "Spring", "price": 4.50, "marketing": 7, "customer_sentiment": 8, "predicted_success": 1},
                {"cookie_flavor": "Pumpkin Chocolate Chip", "seasonality": "Fall", "price": 4.00, "marketing": 8, "customer_sentiment": 9, "predicted_success": 1},
                {"cookie_flavor": "Cornbread Honey Butter", "seasonality": "Winter", "price": 4.25, "marketing": 6, "customer_sentiment": 7, "predicted_success": 0}
            ]
            for entry in crumbl_sample_data:
                new_entry = CookieSalesPrediction(**entry)
                new_entry.create()

            predictions = CookieSalesPrediction.query.all()  # Re-fetch data after adding samples

        # Convert data to NumPy arrays
        X = np.array([[hash(p.cookie_flavor) % 1000, hash(p.seasonality) % 1000, p.price, p.marketing, p.customer_sentiment] 
                      for p in predictions])
        y = np.array([p.predicted_success for p in predictions])

        # Train a random forest model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)

        # Save the trained model
        joblib.dump(model, "titanic_cookie_model.pkl")

        return jsonify({'message': 'Model trained successfully with initial sample data if needed.'})


# Add resources to API
api.add_resource(CookiePredictionAPI, '/predict')
api.add_resource(CookieTrainingAPI, '/train')
