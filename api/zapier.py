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
    """
    Return low stock alert for a specific item based on threshold.
    This endpoint is designed to be polled by Zapier to create automatic low stock alerts.
    """
    try:
        # Find the specific item
        item = Flashcard.query.get(item_id)
        
        if not item:
            return jsonify({"error": f"Item with ID {item_id} not found"}), 404
            
        # Get the deck (category) information
        category = "Uncategorized"
        if item._deck_id:
            deck = Deck.query.filter_by(id=item._deck_id).first()
            if deck:
                category = deck._title
        
        # Parse quantity from content (format: "quantity / description")
        low_stock_item = None
        try:
            # Parse the quantity from the content field
            if "/" in item._content:
                parts = item._content.split("/", 1)
                quantity = int(parts[0].strip())
                
                # Check if stock is below threshold
                if quantity < threshold:
                    low_stock_item = {
                        "id": item.id,
                        "name": item._title,
                        "quantity": quantity,
                        "threshold": threshold,
                        "category": category,
                        "description": parts[1].strip() if len(parts) > 1 else ""
                    }
        except (ValueError, IndexError) as e:
            current_app.logger.error(f"Error parsing item content: {str(e)}")
        
        # Return response with alert info and current timestamp
        return jsonify({
            "has_low_stock": low_stock_item is not None,
            "item": low_stock_item,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in low stock API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@zapier_api.route('/low-stock', methods=['GET', 'OPTIONS'])
@cross_origin(origins="*", methods=["GET", "OPTIONS"])
def get_all_low_stock():
    """
    Return all items with stock below threshold.
    This endpoint is designed to be polled by Zapier to create automatic low stock alerts.
    """
    try:
        # Get threshold from request parameters or use default
        threshold = request.args.get('threshold', 5, type=int)
        
        # Query for all flashcards
        items = Flashcard.query.all()
        
        low_stock_items = []

        for item in items:
            try:
                # Skip items without content
                if not item._content:
                    continue
                    
                # Parse the quantity from the content field
                if "/" in item._content:
                    parts = item._content.split("/", 1)
                    if len(parts) >= 1:
                        try:
                            quantity = int(parts[0].strip())
                            
                            # Check if stock is below threshold
                            if quantity < threshold:
                                # Get deck name if available
                                category = "Uncategorized"
                                if item._deck_id:
                                    deck = Deck.query.filter_by(id=item._deck_id).first()
                                    if deck:
                                        category = deck._title
                                
                                # Add to low stock items
                                low_stock_items.append({
                                    "id": item.id,
                                    "name": item._title,
                                    "quantity": quantity,
                                    "threshold": threshold,
                                    "category": category,
                                    "description": parts[1].strip() if len(parts) > 1 else ""
                                })
                        except (ValueError, IndexError):
                            # Skip if quantity is not a valid integer
                            continue
            except Exception as e:
                current_app.logger.error(f"Error processing item {item.id}: {str(e)}")
                continue
        
        # Return properly formatted JSON for Zapier with current timestamp
        return jsonify({
            "low_stock_items": low_stock_items,
            "count": len(low_stock_items),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Error in low stock API: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Add a simple test endpoint
@zapier_api.route('/test', methods=['GET'])
@cross_origin(origins="*")
def test_endpoint():
    """Simple test endpoint to verify the blueprint is working"""
    return jsonify({"message": "Zapier API is working!", "timestamp": datetime.now().isoformat()})