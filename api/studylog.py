from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd
import joblib
import requests
from datetime import datetime, timedelta
from api.jwt_authorize import token_required
from __init__ import db

# Blueprint setup
prediction_api = Blueprint('prediction_api', __name__, url_prefix='/api')

# Enable CORS
CORS(
    prediction_api,
    resources={r"/*": {"origins": ["http://127.0.0.1:4887", "https://zafeera123.github.io"]}},
    supports_credentials=True
)

api = Api(prediction_api)

# AI Model and Data Storage
model = LinearRegression()
historical_data = pd.DataFrame(columns=["date", "sales_quantity", "inventory_quantity"])

# Inventory API Endpoint (Replace with actual API URL)
INVENTORY_API_URL = "https://optivize.stu.nighthawkcodingsociety.com/api/flashcard/<int:flashcard_id>"

class SalesPredictionAPI:
    class _Predict(Resource):
        @token_required()
        @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
        def get(self):
            """Fetch inventory data and predict future sales dynamically."""
            try:
                # Fetch inventory data from the Inventory API
                response = requests.get(INVENTORY_API_URL)
                if response.status_code != 200:
                    return {'message': 'Failed to fetch inventory data'}, 500
                
                inventory_data = response.json()

                # Convert to DataFrame
                inventory_df = pd.DataFrame(inventory_data)
                inventory_df['date'] = pd.to_datetime(inventory_df['date'])
                inventory_df['month'] = inventory_df['date'].dt.month

                # Ensure sales data exists; otherwise, estimate it
                if 'sales_quantity' not in inventory_df:
                    inventory_df['sales_quantity'] = inventory_df['inventory_quantity'].diff().fillna(0).abs()

                # Update historical data and retrain model
                global historical_data
                historical_data = pd.concat([historical_data, inventory_df], ignore_index=True).drop_duplicates()

                # Features & Target
                if len(historical_data) < 10:
                    return {'message': 'Not enough data to train the model yet.'}, 400

                X = historical_data[['inventory_quantity', 'month']]
                y = historical_data['sales_quantity']

                # Train the model
                model.fit(X, y)
                joblib.dump(model, 'sales_model.pkl')

                # Predict future sales
                latest_inventory = inventory_df['inventory_quantity'].iloc[-1]
                future_inventory = np.array([[latest_inventory, inventory_df['month'].iloc[-1]]])
                predicted_sales = model.predict(future_inventory)[0]

                return jsonify({
                    'predicted_sales': float(predicted_sales),
                    'latest_inventory': int(latest_inventory),
                    'model_updated': True
                })

            except Exception as e:
                return {'message': f"An error occurred: {str(e)}"}, 500

    class _GenerateSyntheticData(Resource):
        """Generates synthetic sales data based on trends for improved prediction accuracy."""
        @token_required()
        @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
        def post(self):
            try:
                global historical_data

                # Generate past 30 days of synthetic data if missing
                today = datetime.now()
                dates = [today - timedelta(days=i) for i in range(30)]

                synthetic_data = []
                for date in dates:
                    inventory_quantity = np.random.randint(50, 500)
                    sales_quantity = max(0, int(np.random.normal(inventory_quantity * 0.2, 10)))

                    synthetic_data.append({
                        "date": date.strftime('%Y-%m-%d'),
                        "inventory_quantity": inventory_quantity,
                        "sales_quantity": sales_quantity
                    })

                # Add synthetic data
                synthetic_df = pd.DataFrame(synthetic_data)
                synthetic_df['date'] = pd.to_datetime(synthetic_df['date'])
                synthetic_df['month'] = synthetic_df['date'].dt.month
                historical_data = pd.concat([historical_data, synthetic_df], ignore_index=True).drop_duplicates()

                return jsonify({'message': 'Synthetic data generated', 'data_count': len(synthetic_df)})

            except Exception as e:
                return {'message': f"An error occurred: {str(e)}"}, 500

# API Routes
api.add_resource(SalesPredictionAPI._Predict, '/sales_predict')
api.add_resource(SalesPredictionAPI._GenerateSyntheticData, '/generate_synthetic_data')

# Load saved model if available
try:
    model = joblib.load('sales_model.pkl')
except:
    print("No pre-trained model found, using default model.")
