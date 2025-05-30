from flask import Blueprint, request, redirect, session, jsonify
import os, requests
from urllib.parse import urlencode
from model.flashcard import Flashcard
from model.deck import Deck
from flask_login import login_required, current_user

google_api = Blueprint('google_api', __name__, url_prefix='/google')

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI_LOCAL = os.getenv("GOOGLE_REDIRECT_URI_LOCAL")
GOOGLE_REDIRECT_URI_DEPLOYED = os.getenv("GOOGLE_REDIRECT_URI_DEPLOYED")
FRONTEND_REDIRECT_LOCAL = os.getenv("FRONTEND_REDIRECT_LOCAL")
FRONTEND_REDIRECT_DEPLOYED = os.getenv("FRONTEND_REDIRECT_DEPLOYED")

@google_api.route('/connect')
def google_connect():
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI_DEPLOYED if "onrender.com" in request.host else GOOGLE_REDIRECT_URI_LOCAL,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/spreadsheets.readonly",
        "access_type": "offline",
        "prompt": "consent"
    }
    return redirect(f"{auth_url}?{urlencode(params)}")

@google_api.route('/callback')
@login_required
def google_callback():
    code = request.args.get("code")
    if not code:
        return "Missing code", 400

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI_DEPLOYED if "onrender.com" in request.host else GOOGLE_REDIRECT_URI_LOCAL,
        "grant_type": "authorization_code"
    }

    r = requests.post(token_url, data=data)
    token_data = r.json()

    if "access_token" not in token_data:
        return jsonify(token_data), 400

    session["google_access_token"] = token_data["access_token"]
    frontend_redirect = FRONTEND_REDIRECT_DEPLOYED if "onrender.com" in request.host else FRONTEND_REDIRECT_LOCAL
    return redirect(f"{frontend_redirect}?import=1")


@google_api.route('/import', methods=['POST'])
@login_required
def import_from_google_sheets():
    from __init__ import db
    import re

    sheet_id = request.json.get("sheet_id")
    access_token = session.get("google_access_token")

    if not access_token or not sheet_id:
        return jsonify({"error": "Missing token or sheet ID"}), 400

    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/A1:Z1000"
    r = requests.get(url, headers=headers)
    data = r.json()

    values = data.get("values", [])
    if not values or len(values) < 2:
        return jsonify({"error": "No rows found"}), 400

    rows = values  


    # Detect important columns
    title_index = next((i for i, h in enumerate(headers) if "title" in h.lower() or "name" in h.lower()), 0)
    quantity_index = next((i for i, h in enumerate(headers) if re.search(r'amount|qty|quantity|stock|count', h.lower())), None)

    group_name = "Google Sheet Import"
    deck = Deck.query.filter_by(_title=group_name, _user_id=current_user.id).first()
    if not deck:
        deck = Deck(title=group_name, user_id=current_user.id)
        db.session.add(deck)
        db.session.commit()

    success_count = 0
    for row in rows:
        try:
            if not row or not row[0].strip():
                continue

            title = row[0].strip()
            quantity = ""
            description_parts = []

            for cell in row[1:]:
                if cell.strip().isdigit() and not quantity:
                    quantity = cell.strip()
                else:
                    description_parts.append(cell.strip())

            description = " ".join(description_parts).strip()
            content = f"{quantity} / {description}" if quantity else description

            flashcard = Flashcard(
                title=title,
                content=content,
                user_id=current_user.id,
                deck_id=deck.id
            )

            db.session.add(flashcard)
            db.session.commit()

            print(f"✅ Imported: {title} | {content}")
            success_count += 1

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error with row {row}: {e}")


    return jsonify({"message": f"Imported {success_count} items to group: {group_name}"}), 200
