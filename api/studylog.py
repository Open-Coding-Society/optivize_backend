from unicodedata import category
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import pandas as pd
from model.studylog import productSalesPrediction, db
from datetime import datetime

product_api = Blueprint('product_api', __name__, url_prefix='/api')
api = Api(product_api)

# Enable CORS
CORS(product_api, resources={r"/*": {"origins": ["http://127.0.0.1:4887", "https://zafeera123.github.io"]}},
     supports_credentials=True)

# Product categories
# Updated Product categories
PRODUCT_CATEGORIES = {
    'fruits': {'base_price': 3.50, 'seasonality': 'seasonal'},
    'vegetables': {'base_price': 2.50, 'seasonality': 'seasonal'},
    'electronics': {'base_price': 199.99, 'seasonality': 'year-round'},
    'clothing': {'base_price': 29.99, 'seasonality': 'seasonal'},
    'sports': {'base_price': 49.99, 'seasonality': 'year-round'},
    'home_goods': {'base_price': 39.99, 'seasonality': 'year-round'},
    'toys': {'base_price': 19.99, 'seasonality': 'holiday'},
    'books': {'base_price': 14.99, 'seasonality': 'year-round'}
}

# Load Model
try:
    model = joblib.load("titanic_product_model.pkl")
except FileNotFoundError:
    model = None

def determine_category(product_type):
    """General category detection based on product type keywords"""
    product_type = product_type.lower()
    
    if any(x in product_type for x in ['apple', 'banana', 'berry', 'fruit', 'orange', 'grape', 'kiwi']):
        return 'fruits'
    elif any(x in product_type for x in ['tomato', 'carrot', 'lettuce', 'vegetable', 'cucumber', 'pepper', 'broccoli']):
        return 'vegetables'
    elif any(x in product_type for x in ['phone', 'laptop', 'camera', 'electronic', 'PC', 'tablet', 'gadget', 'headphone', 'speaker', 'TV', 'headset']):
        return 'electronics'
    elif any(x in product_type for x in ['shirt', 'pants', 'dress', 'jacket', 'jeans', 'sneakers', 'sweater', 'clothing', 'socks', 'hat', 'scarf', 'gloves']):
        return 'clothing'
    elif any(x in product_type for x in ['ball', 'racket', 'bat', 'sport', 'exercise', 'fitness', 'gear', 'equipment']):
        return 'sports'
    elif any(x in product_type for x in ['furniture', 'decor', 'kitchen', 'home', 'decoration', 'lamp', 'appliance', 'utensil']):
        return 'home_goods'
    elif any(x in product_type for x in ['toy', 'game', 'doll', 'lego', 'action figure', 'puzzle', 'board game', 'stuffed animal']):
        return 'toys'
    elif any(x in product_type for x in ['book', 'novel', 'textbook', 'magazine', 'comic', 'literature', 'story', 'guide']):
        return 'books'
    return 'miscellaneous'  # Default category
class productPredictionAPI(Resource):
    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def post(self):
        """Enhanced prediction with comprehensive insights"""
        data = request.get_json()
        
        # Validation
        required_fields = ['product_type', 'seasonality', 'price', 'marketing', 'distribution_channels']
        if missing := [f for f in required_fields if f not in data]:
            return {'message': 'Missing required fields', 'missing': missing}, 400

        if not model:
            return {'message': 'Model not trained. Train first with /api/train'}, 503

        try:
            # Prepare input
            input_data = np.array([[
                hash(data['product_type']) % 1000,
                hash(data['seasonality']) % 1000,
                float(data['price']),
                int(data['marketing']),
                float(data['distribution_channels'])
            ]])
            
            # Get prediction score (0-100)
            success_score = float(model.predict(input_data)[0])
            success_score = max(0, min(100, success_score))  # Ensure within bounds
            is_success = success_score >= 70
            category = determine_category(data['product_type'])

            # Get historical data for insights
            historical_data = self._get_historical_insights(category)
            price_stats = self._get_price_stats(category)
            marketing_stats = self._get_marketing_stats()

            # Generate comprehensive insights
            insights = {
                'score_analysis': self._get_score_analysis(success_score),
                'price_analysis': self._get_price_analysis(float(data['price']), price_stats, category),
                'marketing_analysis': self._get_marketing_analysis(int(data['marketing']), marketing_stats),
                'seasonality_analysis': self._get_seasonality_analysis(data['seasonality'], category),
                'success_probability': self._calculate_success_probability(success_score),
                'recommendations': self._generate_recommendations(data, success_score, category)
            }

            # Save to DB
            prediction = productSalesPrediction(
                product_type=data['product_type'],
                seasonality=data['seasonality'],
                price=float(data['price']),
                marketing=int(data['marketing']),
                distribution_channels=float(data['distribution_channels']),
                predicted_success=is_success,
                success_score=success_score,
                product_category=category
            )
            
            if not prediction.create():
                raise Exception("Failed to save prediction")

            return jsonify({
                'success': True,
                'score': round(success_score, 2),
                'is_success': is_success,
                'category': category,
                'insights': insights,
                'database_id': prediction.id
            })

        except Exception as e:
            return {'message': f'Prediction failed: {str(e)}'}, 500

    def _get_historical_insights(self, category):
        """Get historical data for the category"""
        successful = productSalesPrediction.query.filter(
            productSalesPrediction.product_category == category,
            productSalesPrediction.success_score >= 70
        ).all()
        
        unsuccessful = productSalesPrediction.query.filter(
            productSalesPrediction.product_category == category,
            productSalesPrediction.success_score < 70
        ).all()
        
        return {
            'successful_count': len(successful),
            'unsuccessful_count': len(unsuccessful),
            'success_rate': len(successful) / (len(successful) + len(unsuccessful)) * 100 if (successful or unsuccessful) else None
        }

    def _get_price_stats(self, category):
        """Calculate price statistics for category with better defaults"""
        prices = [p.price for p in productSalesPrediction.query.filter(
            productSalesPrediction.product_category == category,
            productSalesPrediction.success_score >= 70
        ).all()]
        
        # Use category base price if no historical data
        if not prices:
            base_price = PRODUCT_CATEGORIES.get(category, {}).get('base_price', 10.0)  # Default $10 if no category
            return {
                'average': base_price,
                'min': base_price * 0.8,  # 20% below
                'max': base_price * 1.2,  # 20% above
                'std_dev': base_price * 0.1  # 10% std dev
            }
        
        return {
            'average': round(float(np.mean(prices)), 2),
            'min': round(float(min(prices)), 2),
            'max': round(float(max(prices)), 2),
            'std_dev': round(float(np.std(prices)), 2) if len(prices) > 1 else (max(prices)-min(prices))/2
        }
        
    def _get_marketing_stats(self):
        """Calculate overall marketing stats"""
        marketing_scores = [p.marketing for p in productSalesPrediction.query.filter(
            productSalesPrediction.success_score >= 70
        ).all()] or [7]  # Default if no data
        
        return {
            'average': round(float(np.mean(marketing_scores)), 1),
            'min': int(min(marketing_scores)),
            'max': int(max(marketing_scores))
        }

    def _get_score_analysis(self, score):
        """Analyze the success score"""
        ranges = [
            (90, 100, "Exceptional", "Highly likely to succeed"),
            (80, 89, "Very Strong", "Very high chance of success"),
            (70, 79, "Strong", "Good chance of success"),
            (60, 69, "Moderate", "Needs some improvements"),
            (50, 59, "Marginal", "Significant improvements needed"),
            (0, 49, "Poor", "High risk of failure")
        ]
        
        for lower, upper, label, description in ranges:
            if lower <= score <= upper:
                return {
                    'label': label,
                    'range': f"{lower}-{upper}",
                    'description': description,
                    'risk_level': 100 - score
                }

    def _get_price_analysis(self, current_price, price_stats, category):
        """Analyze price positioning for general products"""
        diff = current_price - price_stats['average']
        diff_pct = (diff / price_stats['average']) * 100 if price_stats['average'] else 0
        
        # Different thresholds for different categories
        if category in ['electronics', 'sports']:
            premium_threshold = price_stats['std_dev'] * 2
        else:
            premium_threshold = price_stats['std_dev'] * 1.5
        
        if diff > premium_threshold:
            position = "Premium"
            advice = f"Priced {abs(diff_pct):.1f}% above category average"
        elif diff > 0:
            position = "High-end"
            advice = f"Priced {abs(diff_pct):.1f}% above category average"
        elif abs(diff) <= price_stats['std_dev']:
            position = "Competitive"
            advice = "Competitively priced for this category"
        else:
            position = "Value"
            advice = f"Priced {abs(diff_pct):.1f}% below category average"
        
        return {
            'current_price': current_price,
            'category_average': price_stats['average'],
            'position': position,
            'price_difference': round(diff, 2),
            'percentage_difference': round(diff_pct, 1),
            'advice': advice,
            'price_range': {
                'min': price_stats['min'],
                'max': price_stats['max']
            }
        }

    def _get_marketing_analysis(self, current_marketing, marketing_stats):
        """Analyze marketing effectiveness"""
        diff = current_marketing - marketing_stats['average']
        
        if current_marketing >= marketing_stats['average'] + 2:
            rating = "Excellent"
            advice = "More than sufficient marketing support"
        elif current_marketing >= marketing_stats['average']:
            rating = "Good"
            advice = "Adequate marketing investment"
        else:
            rating = "Below Average"
            advice = f"Consider increasing by {round(abs(diff), 1)} points"
        
        return {
            'current': current_marketing,
            'average_successful': marketing_stats['average'],
            'rating': rating,
            'difference': round(diff, 1),
            'advice': advice,
            'effective_range': {
                'min': marketing_stats['min'],
                'max': marketing_stats['max']
            }
        }

    def _get_seasonality_analysis(self, current_season, category):
        """Analyze seasonality match for general products"""
        category_data = PRODUCT_CATEGORIES.get(category, {})
        expected_season = category_data.get('seasonality', 'year-round')
        
        if expected_season == 'year-round':
            return {
                'match': True,
                'message': "This category performs well year-round",
                'impact': "No seasonal impact expected"
            }
        
        is_match = expected_season.lower() in current_season.lower()
        
        return {
            'match': is_match,
            'current_season': current_season,
            'recommended_season': expected_season,
            'message': "Perfect season match" if is_match else f"Best season: {expected_season}",
            'impact': "Potential seasonal uplift" if is_match else "Possible seasonal performance dip"
        }

    def _calculate_success_probability(self, score):
        """Calculate probability ranges"""
        base_prob = score / 100
        lower = max(0, base_prob - 0.15)
        upper = min(1, base_prob + 0.15)
        return {
            'range': f"{int(lower*100)}-{int(upper*100)}%",
            'confidence': "High" if (upper-lower) < 0.2 else "Medium"
        }
        
    def _generate_recommendations(self, data, score, category):
        """Generate actionable recommendations for products with null checks and improved logic"""
        recs = []
        category_data = PRODUCT_CATEGORIES.get(category, {})
        price = float(data.get('price', 0))
        marketing = int(data.get('marketing', 0))
        distribution = float(data.get('distribution_channels', 0))
        
        # General score-based recommendations
        if score >= 80:
            recs.append("Proceed with full-scale launch")
            if price > category_data.get('base_price', 0) * 1.1:
                recs.append("Premium pricing strategy validated")
        elif score >= 70:
            recs.append("Proceed with standard launch")
            recs.append("Run targeted marketing campaign")
        elif score >= 60:
            recs.append("Conduct small test market first")
            recs.append("Optimize product before full launch")
        else:
            recs.append("Re-evaluate product concept")
            recs.append("Conduct market research")

        # Price recommendations (only if we have valid price data)
        if price > 0 and category_data.get('base_price'):
            base_price = category_data['base_price']
            price_diff_pct = ((price - base_price) / base_price) * 100
            
            if price > base_price * 1.2:
                recs.append(f"Consider reducing price from ${price:.2f} to ~${base_price * 1.1:.2f} (+10% category average)")
            elif price > base_price * 1.1:
                recs.append(f"Price is {price_diff_pct:.1f}% above category average - ensure premium positioning")
            elif price < base_price * 0.9:
                recs.append(f"Consider increasing price from ${price:.2f} to ~${base_price:.2f} (category average)")
            else:
                recs.append("Price is well positioned within category range")

        # Marketing recommendations
        if marketing > 0:
            if marketing < 5:
                recs.append(f"Increase marketing from {marketing}/10 to at least 6/10 for better visibility")
            elif marketing < 7:
                recs.append(f"Marketing at {marketing}/10 - consider boosting to 8/10 for stronger impact")
            elif marketing > 8:
                recs.append(f"Marketing at {marketing}/10 - maintain strong promotional support")

        # Distribution recommendations
        if distribution > 0:
            if distribution < 5:
                recs.append(f"Expand distribution from {distribution}/10 to at least 7/10 for better reach")
            elif distribution < 7:
                recs.append(f"Distribution at {distribution}/10 - aim for 8/10 for optimal availability")
            else:
                recs.append(f"Distribution at {distribution}/10 - excellent channel coverage")

        # Seasonal recommendations (only if seasonality exists)
        if category_data.get('seasonality'):
            current_season = data.get('seasonality', '').lower()
            recommended_season = category_data['seasonality'].lower()
            
            if recommended_season == 'year-round':
                recs.append("This product category performs well year-round")
            elif recommended_season in current_season:
                recs.append(f"Perfect seasonal timing ({current_season.capitalize()} matches best season)")
            else:
                recs.append(f"Best launched in {recommended_season.capitalize()} (current: {current_season.capitalize()})")

        # Category-specific recommendations
        if category == 'electronics':
            recs.append("Consider extended warranty options for premium positioning")
        elif category == 'fruits':
            recs.append("Highlight freshness and sourcing in marketing")
        elif category == 'sports':
            recs.append("Feature athlete endorsements if applicable")

        # Ensure we don't return empty or None recommendations
        recs = [r for r in recs if r and not (str(r).strip() == 'None')]
        
        return recs[:10]  # Return maximum 10 most relevant recommendations

class productTrainingAPI(Resource):
    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def post(self):
        data = request.get_json()
        
        if not data or 'samples' not in data:
            return {'message': 'Missing samples data'}, 400

        valid_samples = []
        required_fields = ['product_type', 'seasonality', 'price', 
                         'marketing', 'distribution_channels', 'success_score']
        
        for sample in data['samples']:
            if not all(field in sample for field in required_fields):
                continue
            
            try:
                category = determine_category(sample['product_type'])
                success_score = float(sample['success_score'])
                
                prediction = productSalesPrediction(
                    product_type=sample['product_type'],
                    seasonality=sample['seasonality'],
                    price=float(sample['price']),
                    marketing=int(sample['marketing']),
                    distribution_channels=float(sample['distribution_channels']),
                    predicted_success=success_score >= 70,
                    success_score=success_score,
                    product_category=category
                )
                
                if prediction.create():
                    valid_samples.append({
                        'type_hash': hash(sample['product_type']) % 1000,
                        'season_hash': hash(sample['seasonality']) % 1000,
                        'price': float(sample['price']),
                        'marketing': int(sample['marketing']),
                        'distribution': float(sample['distribution_channels']),
                        'success_score': success_score
                    })
            except Exception as e:
                print(f"Skipping invalid sample: {str(e)}")

        if len(valid_samples) < 5:
            return {'message': f'Insufficient data (need 5, got {len(valid_samples)})'}, 400

        try:
            df = pd.DataFrame(valid_samples)
            X = df[['type_hash', 'season_hash', 'price', 'marketing', 'distribution']]
            y = df['success_score'].clip(0, 100)  # Ensure scores are between 0-100

            global model
            model = RandomForestRegressor(
                n_estimators=200,
                min_samples_leaf=3,
                max_depth=10,
                random_state=42,
                max_features=0.8
            )
            model.fit(X, y)
            
            joblib.dump(model, "titanic_product_model.pkl")

            y_pred = model.predict(X)
            return jsonify({
                'success': True,
                'samples_used': len(valid_samples),
                'r2_score': round(r2_score(y, y_pred), 4),
                'mae': round(mean_absolute_error(y, y_pred), 2),
                'categories_trained': len(set(p.product_category for p in productSalesPrediction.query.all()))
            })

        except Exception as e:
            return {'message': f'Training failed: {str(e)}'}, 500

class productHistoryAPI(Resource):
    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def get(self):
        try:
            predictions = productSalesPrediction.query.order_by(productSalesPrediction.date_created.desc()).all()
            return jsonify([p.read() for p in predictions])
        except Exception as e:
            return {'message': f'Failed to fetch history: {str(e)}'}, 500

# Register endpoints
api.add_resource(productPredictionAPI, '/predict')
api.add_resource(productTrainingAPI, '/train')
api.add_resource(productHistoryAPI, '/history')