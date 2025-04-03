import logging
import joblib
import numpy as np
from pandas import DataFrame
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from sklearn.ensemble import RandomForestClassifier
from model.studylog import CookieSalesPrediction

# Initialize Blueprint and API
cookie_api = Blueprint('cookie_api', __name__, url_prefix='/api')
api = Api(cookie_api)
CORS(cookie_api, resources={r"/*": {"origins": ["http://127.0.0.1:4887", "https://zafeera123.github.io"]}}, supports_credentials=True)

MODEL_PATH = "cookie_sales_model.pkl"

# Load Model
try:
    model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully.")
except Exception as e:
    model = None
    print(f"⚠️ Failed to load model: {e}")

class CookiePredictionAPI(Resource):
    @cross_origin()
    def post(self):
        try:
            if not request.is_json:
                return jsonify({'message': 'Invalid request: JSON data required'}), 400

            data = request.get_json()
            print("📥 Received data:", data)

            required_fields = ['cookie_flavor', 'price', 'marketing spend']
            if not all(field in data for field in required_fields):
                return jsonify({'message': 'Missing required fields'}), 400

            cookie_flavor = str(data['cookie_flavor']).strip()
            price = float(data['price'])
            marketing = float(data['marketing spend'])

            if model is None:
                return jsonify({'message': 'Model not trained. Please train the model first.'}), 500

            input_data = np.array([[hash(cookie_flavor) % 1000, price, marketing]])
            print("🔢 Input data for model prediction:", input_data)

            success_probability = model.predict_proba(input_data)[0][1] * 100
            print(f"📊 Predicted success probability: {success_probability:.2f}%")

            return jsonify({'success_probability': round(success_probability, 2)})
        except Exception as e:
            print(f"❌ Error during prediction: {e}")
            return jsonify({'message': f"An error occurred during prediction: {str(e)}"}), 500

class CookieTrainingAPI(Resource):
    @cross_origin()
    def post(self):
        try:
            predictions = CookieSalesPrediction.query.all()

            if len(predictions) < 10:
                sample_data = [
                    {"cookie_flavor": "Chocolate Chip", "seasonality": "All Year", "price": 4.00, "marketing": 9, "customer_sentiment": 9, "predicted_success": 1},
                    {"cookie_flavor": "Sugar Cookie", "seasonality": "All Year", "price": 3.75, "marketing": 8, "customer_sentiment": 8, "predicted_success": 1},
                    {"cookie_flavor": "Chocolate Chip", "seasonality": "All Year", "price": 4.00, "marketing": 9, "customer_sentiment": 9, "predicted_success": 1},
                    {"cookie_flavor": "Peanut Butter", "seasonality": "All Year", "price": 3.50, "marketing": 7, "customer_sentiment": 8, "predicted_success": 0.8},
                    {"cookie_flavor": "Oatmeal Raisin", "seasonality": "All Year", "price": 3.75, "marketing": 8, "customer_sentiment": 7, "predicted_success": 0.85},
                    {"cookie_flavor": "Sugar Cookie", "seasonality": "Winter", "price": 2.75, "marketing": 6, "customer_sentiment": 6, "predicted_success": 0.65},
                    {"cookie_flavor": "Chocolate Mint", "seasonality": "Winter", "price": 3.99, "marketing": 10, "customer_sentiment": 10, "predicted_success": 1},
                    {"cookie_flavor": "Snickerdoodle", "seasonality": "All Year", "price": 3.25, "marketing": 5, "customer_sentiment": 5, "predicted_success": 0.5},
                    {"cookie_flavor": "Lemon Drop", "seasonality": "Spring", "price": 3.50, "marketing": 7, "customer_sentiment": 8, "predicted_success": 0.75},
                    {"cookie_flavor": "Double Chocolate", "seasonality": "All Year", "price": 4.25, "marketing": 9, "customer_sentiment": 9, "predicted_success": 0.9},
                    {"cookie_flavor": "Gingerbread", "seasonality": "Winter", "price": 3.00, "marketing": 6, "customer_sentiment": 6, "predicted_success": 0.7},
                    {"cookie_flavor": "Almond Joy", "seasonality": "All Year", "price": 4.00, "marketing": 8, "customer_sentiment": 8, "predicted_success": 0.8},
                    {"cookie_flavor": "Carrot Cake", "seasonality": "Fall", "price": 3.25, "marketing": 5, "customer_sentiment": 4, "predicted_success": 0.45},
                    {"cookie_flavor": "Coconut Cream", "seasonality": "Spring", "price": 3.75, "marketing": 8, "customer_sentiment": 7, "predicted_success": 0.85},
                    {"cookie_flavor": "Maple Pecan", "seasonality": "Fall", "price": 4.25, "marketing": 9, "customer_sentiment": 8, "predicted_success": 0.9},
                    {"cookie_flavor": "Pumpkin Spice", "seasonality": "Fall", "price": 3.50, "marketing": 7, "customer_sentiment": 7, "predicted_success": 0.75},
                    {"cookie_flavor": "Toffee Crunch", "seasonality": "All Year", "price": 3.99, "marketing": 9, "customer_sentiment": 9, "predicted_success": 0.95},
                    {"cookie_flavor": "Mango", "seasonality": "Summer", "price": 3.50, "marketing": 7, "customer_sentiment": 6, "predicted_success": 0.75},
                    {"cookie_flavor": "Blueberry", "seasonality": "Summer", "price": 3.75, "marketing": 8, "customer_sentiment": 7, "predicted_success": 0.85},
                    {"cookie_flavor": "Peach", "seasonality": "Summer", "price": 3.25, "marketing": 5, "customer_sentiment": 4, "predicted_success": 0.45},
                    {"cookie_flavor": "Cherry", "seasonality": "Summer", "price": 3.50, "marketing": 7, "customer_sentiment": 6, "predicted_success": 0.75},
                    {"cookie_flavor": "Raspberry", "seasonality": "Summer", "price": 3.75, "marketing": 8, "customer_sentiment": 7, "predicted_success": 0.85},
                    {"cookie_flavor": "Strawberry", "seasonality": "Summer", "price": 3.25, "marketing": 5, "customer_sentiment": 4, "predicted_success": 0.45},
                    {"cookie_flavor": "Pineapple", "seasonality": "Summer", "price": 3.50, "marketing": 7, "customer_sentiment": 6, "predicted_success": 0.75},
            ]
                for entry in sample_data:
                    new_entry = CookieSalesPrediction(**entry)
                    new_entry.create()
                predictions = CookieSalesPrediction.query.all()

            X = np.array([[hash(p.cookie_flavor) % 1000, p.price, p.marketing] for p in predictions])
            y = np.array([p.predicted_success for p in predictions])

            global model
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X, y)

            joblib.dump(model, MODEL_PATH)
            print("✅ Model trained and saved successfully.")

            return jsonify({'message': 'Model trained successfully.'})
        except Exception as e:
            print(f"❌ Error during training: {e}")
            return jsonify({'message': f"An error occurred during training: {str(e)}"}), 500

# Add resources to API
api.add_resource(CookiePredictionAPI, '/predict')
api.add_resource(CookieTrainingAPI, '/train')
