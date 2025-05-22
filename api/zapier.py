from flask import Blueprint, jsonify, request, current_app
from flask_cors import cross_origin, CORS
from model.flashcard import Flashcard
from model.deck import Deck
from __init__ import db
from datetime import datetime

# Create a Blueprint for the Zapier API
zapier_api = Blueprint('zapier_api', __name__, url_prefix='/api/zapier')

# Enable CORS for the entire blueprint
CORS(zapier_api, origins="*", methods=["GET", "POST", "OPTIONS"])

@zapier_api.route('/low-stock/<int:item_id>/<int:threshold>', methods=['GET', 'OPTIONS'])
@cross_origin(origins="*", methods=["GET", "OPTIONS"])  
def get_low_stock_for_item(item_id, threshold):
    try:
        item = Flashcard.query.get(item_id)
        if not item:
            return jsonify([]), 200
            
        category = "Uncategorized"
        if item._deck_id:
            deck = Deck.query.filter_by(id=item._deck_id).first()
            if deck:
                category = deck._title
        
        try:
            if "/" in item._content:
                parts = item._content.split("/", 1)
                quantity = int(parts[0].strip())
                
                if quantity < threshold:
                    return jsonify([{
                        "id": f"alert_{item.id}_{threshold}_{int(datetime.now().timestamp())}",
                        "name": item._title,
                        "quantity": quantity,
                        "threshold": threshold,
                        "category": category,
                        "description": parts[1].strip() if len(parts) > 1 else "",
                        "message": f"LOW STOCK: {item._title} has {quantity} items (below {threshold})"
                    }])
        except (ValueError, IndexError):
            pass
        
        return jsonify([])
        
    except Exception as e:
        return jsonify([]), 500