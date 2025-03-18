from flask import Blueprint, jsonify
from datetime import datetime, timedelta

# hello

countdown_api = Blueprint('countdown_api', __name__, url_prefix='/api')

@countdown_api.route('/countdown', methods=['GET'])
def get_countdown():
    """
    Calculate the countdown to the weekend (Saturday, 12:00 AM).
    """
    now = datetime.now()
    # Get the upcoming Saturday
    days_until_saturday = (5 - now.weekday()) % 7  # Saturday is day 5 (0 = Monday)
    next_saturday = now + timedelta(days=days_until_saturday)
    next_saturday_midnight = next_saturday.replace(hour=0, minute=0, second=0, microsecond=0)

    # Calculate the time difference
    time_remaining = next_saturday_midnight - now
    hours, remainder = divmod(time_remaining.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    # Return the countdown to the weekend
    countdown_to_saturday = { # BREAKPOINT
        "days": time_remaining.days,
        "hours": int(hours),
        "minutes": int(minutes),
        "seconds": int(seconds)
    }

    # Get the upcoming Monday (next week, 12:00 AM)
    days_until_monday = (0 - now.weekday()) % 7  # Monday is day 0
    next_monday = now + timedelta(days=days_until_monday)
    next_monday_midnight = next_monday.replace(hour=0, minute=0, second=0, microsecond=0)

    # Calculate the time difference for Monday
    time_until_monday = next_monday_midnight - now
    hours_monday, remainder_monday = divmod(time_until_monday.total_seconds(), 3600)
    minutes_monday, seconds_monday = divmod(remainder_monday, 60)

    # Return the countdown to Monday
    countdown_to_monday = { # BREAKPOINT
        "days": time_until_monday.days,
        "hours": int(hours_monday),
        "minutes": int(minutes_monday),
        "seconds": int(seconds_monday)
    }

    # Return both countdowns as a JSON response
    return jsonify({
        "countdown_to_saturday": countdown_to_saturday,
        "countdown_to_monday": countdown_to_monday
    })
