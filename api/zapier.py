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
def get_low_stock_for_item(item_id, threshold):
    """
    Return low stock alert for a specific item based on threshold.
    This endpoint is designed to be polled by Zapier to create automatic low stock alerts.
    """
    try:
        # Find the specific item
        item = Flashcard.query.get(item_id)
        
        if not item:
            return jsonify([]), 200  # Return empty array, not 404
            
        # Get the deck (category) information
        category = "Uncategorized"
        if item._deck_id:
            deck = Deck.query.filter_by(id=item._deck_id).first()
            if deck:
                category = deck._title
        
        # Parse quantity from content (format: "quantity / description")
        try:
            # Parse the quantity from the content field
            if "/" in item._content:
                parts = item._content.split("/", 1)
                quantity = int(parts[0].strip())
                
                # Check if stock is below threshold
                if quantity < threshold:
                    # Return array format for Zapier
                    return jsonify([{
                        "id": f"alert_{item.id}_{threshold}_{int(datetime.now().timestamp())}",  # Unique ID
                        "item_id": item.id,
                        "name": item._title,
                        "quantity": quantity,
                        "threshold": threshold,
                        "category": category,
                        "description": parts[1].strip() if len(parts) > 1 else "",
                        "message": f"LOW STOCK ALERT: {item._title} has only {quantity} items remaining (below threshold of {threshold})",
                        "timestamp": datetime.now().isoformat()
                    }])
        except (ValueError, IndexError) as e:
            current_app.logger.error(f"Error parsing item content: {str(e)}")
        
        # Return empty array if no alert needed
        return jsonify([])
        
    except Exception as e:
        current_app.logger.error(f"Error in low stock API: {str(e)}")
        return jsonify([]), 500