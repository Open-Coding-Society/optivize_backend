from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from model import CookieSalesPrediction
import joblib
import numpy as np

# Load the Titanic-based predictive model
model = joblib.load("titanic_cookie_model.pkl")

cookie_api = Blueprint('cookie_api', __name__, url_prefix='/api')
api = Api(cookie_api)

# ✅ Enable CORS with credentials support
CORS(cookie_api, resources={r"/*": {"origins": ["http://127.0.0.1:4887", "https://zafeera123.github.io"]}},
     supports_credentials=True)

class CookiePredictionAPI(Resource):
    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def post(self):
        """Predict cookie success based on input data using Titanic-based model."""
        data = request.get_json()

        required_fields = ['cookie_flavor', 'seasonality', 'price', 'marketing', 'customer_sentiment']
        if not all(field in data for field in required_fields):
            return {'message': 'Missing required fields'}, 400

        # Prepare input for the model
        input_data = np.array([[
            hash(data['cookie_flavor']) % 1000,  # Encode categorical feature
            hash(data['seasonality']) % 1000,
            data['price'],
            data['marketing'],
            data['customer_sentiment']
        ]])

        # Predict success (1 for success, 0 for failure)
        prediction = model.predict(input_data)[0]
        predicted_success = bool(prediction)

        # Save the prediction result to the database
        new_prediction = CookieSalesPrediction(
            cookie_flavor=data['cookie_flavor'],
            seasonality=data['seasonality'],
            price=data['price'],
            marketing=data['marketing'],
            customer_sentiment=data['customer_sentiment'],
            predicted_success=predicted_success
        )
        new_prediction.create()

        return jsonify({'success': predicted_success})

# Add the resource to the API
api.add_resource(CookiePredictionAPI, '/predict')
