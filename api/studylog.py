import logging
from pandas import DataFrame
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import numpy as np
import joblib  # For loading the model
from flask import Flask, request, jsonify
from flask_restful import Resource
from flask_cors import cross_origin
from model.studylog import CookieSalesPrediction

cookie_api = Blueprint('cookie_api', __name__, url_prefix='/api')
api = Api(cookie_api)

# ✅ Enable CORS with credentials support
CORS(cookie_api, resources={r"/*": {"origins": ["http://127.0.0.1:4887", "https://zafeera123.github.io"]}},
     supports_credentials=True)
# Load model safely
try:
    model = joblib.load('path/to/your/saved_model.pkl')  # Ensure correct path
    print("✅ Model loaded successfully.")
except Exception as e:
    model = None
    print(f"⚠️ Failed to load model: {e}")

class CookiePredictionAPI(Resource):
    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def post(self):
        """Predict cookie success using a machine learning model."""
        try:
            # Ensure JSON data is received
            if not request.is_json:
                return jsonify({'message': 'Invalid request: JSON data required'}), 400

            data = request.get_json()
            print("📥 Received data:", data)

            # Check if required fields exist
            required_fields = ['cookie_flavor', 'price', 'marketing']
            if not all(field in data for field in required_fields):
                return jsonify({'message': 'Missing required fields'}), 400

            # Validate and convert input values
            try:
                cookie_flavor = str(data['cookie_flavor']).strip()
                price = float(data['price'])  # Convert to float
                marketing = float(data['marketing'])  # Convert to float
            except (ValueError, TypeError):
                return jsonify({'message': 'Invalid input: Price and Marketing must be numbers'}), 400

            # Ensure model is loaded
            if model is None:
                return jsonify({'message': 'Model not trained. Please train the model first.'}), 500

            # Convert input to model format
            input_data = np.array([[
                hash(cookie_flavor) % 1000,  # Hashing flavor to numerical value
                price,
                marketing
            ]])

            print("🔢 Input data for model prediction:", input_data)

            # Predict success probability (0 to 1) and convert to percentage
            success_probability = model.predict_proba(input_data)[0][1] * 100
            print(f"📊 Predicted success probability: {success_probability:.2f}%")

            return jsonify({'success_probability': round(success_probability, 2)})

        except Exception as e:
            print(f"❌ Error during prediction: {e}")
            return jsonify({'message': f"An error occurred during prediction: {str(e)}"}), 500

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
