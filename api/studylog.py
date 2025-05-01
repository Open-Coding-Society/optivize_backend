from importlib.metadata import distribution
import random
from unicodedata import category
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import pandas as pd
from model.studylog import CookieSalesPrediction, db
from datetime import datetime

cookie_api = Blueprint('cookie_api', __name__, url_prefix='/api')
api = Api(cookie_api)

# Enable CORS
CORS(cookie_api, resources={r"/*": {"origins": ["http://127.0.0.1:4887", "https://zafeera123.github.io"]}},
     supports_credentials=True)

# Product categories
PRODUCT_CATEGORIES = {
    'chocolate': {'base_price': 3.75, 'seasonality': 'year-round'},
    'fruit': {'base_price': 3.50, 'seasonality': 'seasonal'},
    'nut': {'base_price': 4.00, 'seasonality': 'year-round'},
    'seasonal': {'base_price': 4.25, 'seasonality': 'holiday'},
    'premium': {'base_price': 4.50, 'seasonality': 'year-round'}
}

# Load Model
try:
    model = joblib.load("titanic_cookie_model.pkl")
except FileNotFoundError:
    model = None

def determine_category(cookie_flavor):
    """Simple category detection based on flavor keywords"""
    flavor = cookie_flavor.lower()
    if any(x in flavor for x in ['chocolate', 'brownie', 'fudge']):
        return 'chocolate'
    elif any(x in flavor for x in ['berry', 'lemon', 'apple']):
        return 'fruit'
    elif any(x in flavor for x in ['nut', 'almond', 'peanut']):
        return 'nut'
    elif any(x in flavor for x in ['pumpkin', 'peppermint', 'holiday']):
        return 'seasonal'
    return 'premium'

class CookiePredictionAPI(Resource):
    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def post(self):
        """Enhanced prediction with comprehensive insights"""
        data = request.get_json()
        
        # Validation
        required_fields = ['cookie_flavor', 'seasonality', 'price', 'marketing', 'distribution_channels']
        if missing := [f for f in required_fields if f not in data]:
            return {'message': 'Missing required fields', 'missing': missing}, 400

        if not model:
            return {'message': 'Model not trained. Train first with /api/train'}, 503

        try:
            
            # 1. EXTRACT ALL INPUTS FIRST
            cookie_flavor = data['cookie_flavor']
            seasonality = data['seasonality']
            price = float(data['price'])  # Defined here
            marketing = int(data['marketing'])  # Defined here
            distribution = float(data['distribution_channels'])
            # 2. DETERMINE CATEGORY AND BASE PRICE
            category = determine_category(cookie_flavor)
            base_price = PRODUCT_CATEGORIES.get(category, {}).get('base_price', 4.0)
            
            
            
            # Prepare input
            input_data = np.array([[
                hash(data['cookie_flavor']) % 1000,
                hash(data['seasonality']) % 1000,
                float(data['price']),
                int(data['marketing']),
                float(data['distribution_channels'])
            ]])
            
            if hasattr(model, 'predict_proba'):
                base_score = float(model.predict_proba(input_data)[0][1]) * 100
            else:
                base_score = float(model.predict(input_data)[0])

                # Marketing boost (0-20 point scale)
            marketing_boost = (int(data['marketing']) / 10) * 20

            # Distribution boost (0-15 point scale)
            distribution_boost = (float(data['distribution_channels']) / 10) * 15

#            Calculate final score
            adjusted_score = base_score + marketing_boost + distribution_boost
            final_score = max(0, min(100, round(adjusted_score)))

        # 4. Enhanced variation logic
            variation = 0
            if 30 < adjusted_score < 70:  # Mid-range gets most variation
                variation = random.gauss(0, 5)  # Normal distribution around 0 (±5%)
            elif adjusted_score >= 70:     # High scores get downward variation
                variation = -abs(random.gauss(0, 3))  # Only negative variation
            else:                         # Low scores get upward variation
                variation = abs(random.gauss(0, 3))   # Only positive variation
            # Final clamp
            final_score = max(0, min(100, final_score))
            is_success = final_score >= 70

            # 6. Ensure full range coverage (edge cases)
            if final_score == 100:
                final_score -= random.randint(0, 3)  # Prevent always max score
            elif final_score == 0:
                final_score += random.randint(0, 3)  # Prevent always min score
            # Get historical data for insights
            historical_data = self._get_historical_insights(category)
            price_stats = self._get_price_stats(category)
            marketing_stats = self._get_marketing_stats()

            # Generate comprehensive insights
            insights = {
                'score_analysis': self._get_score_analysis(is_success),
                'price_analysis': self._get_price_analysis(float(data['price']), price_stats, category),
                'marketing_analysis': self._get_marketing_analysis(int(data['marketing']), marketing_stats),
                'seasonality_analysis': self._get_seasonality_analysis(data['seasonality'], category),
                'success_probability': self._calculate_success_probability(is_success),
                'recommendations': self._generate_recommendations(data, is_success, category)
            }

            # Save to DB
            prediction = CookieSalesPrediction(
            cookie_flavor=data['cookie_flavor'],
            seasonality=data['seasonality'],
            price=float(data['price']),
            marketing=int(data['marketing']),
            distribution_channels=float(data['distribution_channels']),
            predicted_success=is_success,  # Added missing comma here
            success_score=is_success,
            product_category=category
            )
            
            if not prediction.create():
                raise Exception("Failed to save prediction")

            return jsonify({
                'success': True,
                'score': round(is_success, 2),
                'is_success': is_success,
                'category': category,
                'insights': insights,
                'database_id': prediction.id
            })

        except Exception as e:
            return {'message': f'Prediction failed: {str(e)}'}, 500

    def _get_historical_insights(self, category):
        """Get historical data for the category"""
        successful = CookieSalesPrediction.query.filter_by(
            product_category=category,
            predicted_success=True
        ).all()
        
        unsuccessful = CookieSalesPrediction.query.filter_by(
            product_category=category,
            predicted_success=False
        ).all()
        
        return {
            'successful_count': len(successful),
            'unsuccessful_count': len(unsuccessful),
            'success_rate': len(successful) / (len(successful) + len(unsuccessful)) * 100 if (successful or unsuccessful) else None
        }

    def _get_price_stats(self, category):
        """Calculate price statistics for category"""
        prices = [p.price for p in CookieSalesPrediction.query.filter_by(
            product_category=category,
            predicted_success=True
        ).all()] or [PRODUCT_CATEGORIES.get(category, {}).get('base_price', 4.0)]

        return {
            'average': round(float(np.mean(prices)), 2),
            'min': round(float(min(prices)), 2),
            'max': round(float(max(prices)), 2),
            'std_dev': round(float(np.std(prices)), 2) if len(prices) > 1 else 0.5
        }



    def _get_marketing_stats(self):
        """Calculate overall marketing stats"""
        marketing_scores = [p.marketing for p in CookieSalesPrediction.query.filter_by(
            predicted_success=True
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
        """Analyze price positioning"""
        diff = current_price - price_stats['average']
        diff_pct = (diff / price_stats['average']) * 100 if price_stats['average'] else 0
        
        if diff > price_stats['std_dev'] * 1.5:
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
        """Analyze seasonality match"""
        expected_season = PRODUCT_CATEGORIES.get(category, {}).get('seasonality', 'year-round')
        
        if expected_season == 'year-round':
            return {
                'match': True,
                'message': "This category performs well year-round"
            }
        
        is_match = expected_season.lower() in current_season.lower()
        
        return {
            'match': is_match,
            'current_season': current_season,
            'recommended_season': expected_season,
            'message': "Perfect season match" if is_match else f"Best season: {expected_season}",
            'impact': "10-15% potential uplift" if is_match else "Possible 10-15% lower performance"
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
        """Generate actionable recommendations"""
        recs = []
        
        # General recommendations based on score
        if score >= 80:
            recs.append("Proceed with full-scale launch")
            recs.append("Consider premium packaging and pricing")
        elif score >= 70:
            recs.append("Proceed with standard launch")
            recs.append("Run targeted marketing campaign")
        elif score >= 60:
            recs.append("Conduct small test market first")
            recs.append("Optimize product before full launch")
        else:
            recs.append("Reformulate product concept")
            recs.append("Conduct market research")
        # Price recommendations
        price = float(data['price'])
        category_data = PRODUCT_CATEGORIES.get(category, {})
        if price > category_data.get('base_price', 4.0) * 1.2:
            recs.append(f"Consider reducing price to ${category_data.get('base_price', 4.0) * 1.1:.2f} (+10%)")
        elif price < category_data.get('base_price', 4.0) * 0.9:
            recs.append(f"Consider premium version at ${category_data.get('base_price', 4.0):.2f}")
        
        # Marketing recommendations
        marketing = int(data['marketing'])
        if marketing < 6:
            recs.append("Increase marketing budget by 20-30%")
        elif marketing > 8:
            recs.append("Maintain high marketing levels")
        
        # Seasonal recommendations
        if 'seasonal' in category.lower():
            recs.append(f"Launch 2-3 weeks before {PRODUCT_CATEGORIES[category]['seasonality']} season")
        
        return recs
    
    def _get_distribution_stats(self, category):
        """Calculate historical distribution channel statistics for a category"""
        successful_dist = [
            p.distribution_channels 
            for p in CookieSalesPrediction.query.filter_by(
                product_category=category,
                predicted_success=True
            ).all()
        ] or [3.0]  # Default if no data

        return {
            'average': round(float(np.mean(successful_dist)), 2),
            'min': round(float(min(successful_dist)), 2),
            'max': round(float(max(successful_dist)), 2),
            'std_dev': round(float(np.std(successful_dist)), 2) if len(successful_dist) > 1 else 0.5
        }

    def _get_distribution_analysis(self, current_dist, dist_stats, category):
        """Analyze distribution channel effectiveness"""
        diff = current_dist - dist_stats['average']
        diff_pct = (diff / dist_stats['average']) * 100 if dist_stats['average'] else 0

        if diff > dist_stats['std_dev'] * 1.5:
            rating = "Extensive"
            advice = "Consider focusing on highest-performing channels"
        elif diff > 0:
            rating = "Above Average"
            advice = f"Using {abs(diff_pct):.1f}% more channels than typical successes"
        elif abs(diff) <= dist_stats['std_dev']:
            rating = "Optimal"
            advice = "Right mix of distribution channels"
        else:
            rating = "Limited"
            advice = f"Consider adding {abs(round(diff, 2))} more channel types"

        return {
            'current_channels': current_dist,
            'category_average': dist_stats['average'],
            'rating': rating,
            'difference': round(diff, 2),
            'percentage_difference': round(diff_pct, 1),
            'advice': advice,
            'effective_range': {
                'min': dist_stats['min'],
                'max': dist_stats['max']
            }
        }

    def _generate_distribution_recommendations(self, current_dist, dist_stats):
        """Generate specific channel recommendations"""
        recs = []
        if current_dist < dist_stats['average']:
            recs.append(f"Expand from {current_dist} to {round(dist_stats['average'], 1)} channels")
            recs.append("Test 1-2 new retail partners")
        elif current_dist > dist_stats['average'] * 1.2:
            recs.append(f"Optimize your {current_dist} channels (industry avg: {dist_stats['average']})")
            recs.append("Reallocate resources to top-performing channels")
        
        if current_dist < 3:
            recs.append("Add direct-to-consumer online sales")
        elif current_dist > 5:
            recs.append("Audit channel profitability - prune underperformers")
        
        return recs

class CookieTrainingAPI(Resource):
    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def post(self):
        data = request.get_json()
        
        if not data or 'samples' not in data:
            return {'message': 'Missing samples data'}, 400

        valid_samples = []
        required_fields = ['cookie_flavor', 'seasonality', 'price', 
                         'marketing', 'distribution_channels', 'success_score']
        
        for sample in data['samples']:
            if not all(field in sample for field in required_fields):
                continue
            
            try:
                category = determine_category(sample['cookie_flavor'])
                success_score = float(sample['success_score'])
                
                prediction = CookieSalesPrediction(
                    cookie_flavor=sample['cookie_flavor'],
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
                        'flavor_hash': hash(sample['cookie_flavor']) % 1000,
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
            X = df[['flavor_hash', 'season_hash', 'price', 'marketing', 'distribution']]
            
            # --- CRITICAL CHANGES START ---
            # Force 5% increment labels and ensure full range coverage
            y = (df['success_score']
                .clip(0, 100)
                .apply(lambda x: 5 * round(x / 5))  # Round to nearest 5%
                .astype(int))
            
            # Balance the dataset
            low_samples = df[y <= 40].sample(n=20, replace=True) if len(df[y <= 40]) < 20 else df[y <= 40]
            mid_samples = df[(y > 40) & (y < 70)].sample(n=20, replace=True) if len(df[(y > 40) & (y < 70)]) < 20 else df[(y > 40) & (y < 70)]
            high_samples = df[y >= 70]
            
            balanced_df = pd.concat([low_samples, mid_samples, high_samples])
            X = balanced_df[['flavor_hash', 'season_hash', 'price', 'marketing', 'distribution']]
            y = balanced_df['success_score']

            global model
            model = RandomForestRegressor(
                n_estimators=200,
                min_samples_leaf=3,  # More granular predictions
                max_depth=10,        # Capture complex patterns
                random_state=42,
                max_features=0.8     # Better generalization
            )
            model.fit(X, y)
            
            # Verify output distribution
            test_preds = model.predict(X)
            print("Prediction distribution:", np.percentile(test_preds, [0, 10, 25, 50, 75, 90, 100]))
            # --- CRITICAL CHANGES END ---
            
            joblib.dump(model, "titanic_cookie_model.pkl")

            y_pred = model.predict(X)
            return jsonify({
                'success': True,
                'samples_used': len(valid_samples),
                'r2_score': round(r2_score(y, y_pred), 4),
                'mae': round(mean_absolute_error(y, y_pred), 2),
                'categories_trained': len(set(p.product_category for p in CookieSalesPrediction.query.all()))
            })

        except Exception as e:
            return {'message': f'Training failed: {str(e)}'}, 500

class CookieHistoryAPI(Resource):
    @cross_origin(origins=["http://127.0.0.1:4887", "https://zafeera123.github.io"], supports_credentials=True)
    def get(self):
        try:
            predictions = CookieSalesPrediction.query.order_by(CookieSalesPrediction.date_created.desc()).all()
            return jsonify([p.read() for p in predictions])
        except Exception as e:
            return {'message': f'Failed to fetch history: {str(e)}'}, 500

# Register endpoints
api.add_resource(CookiePredictionAPI, '/predict')
api.add_resource(CookieTrainingAPI, '/train')
api.add_resource(CookieHistoryAPI, '/history')