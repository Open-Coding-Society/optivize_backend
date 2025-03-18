from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True, origins='*')  # Allow all origins (*)

# ========================
# Class Schedule
# ========================
schedule = [
    {"Period": 1, "Class": "Honors Medical Intervention", "Start": "08:35", "End": "09:41"},
    {"Period": 2, "Class": "AP CSP", "Start": "09:46", "End": "10:55"},
    {"Period": 3, "Class": "AFA 2", "Start": "11:37", "End": "12:43"},
    {"Period": 4, "Class": "APUSH", "Start": "13:18", "End": "14:24"},
    {"Period": 5, "Class": "AmLit", "Start": "14:29", "End": "15:35"}
]

# ========================
# Helper Functions
# ========================
def get_next_school_day_start():
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    next_school_start = datetime.combine(tomorrow, datetime.strptime("08:35", "%H:%M").time())
    return next_school_start - today

# ========================
# Home Page
# ========================
@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>Welcome to My Flask App</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                background: linear-gradient(to bottom, #87CEEB, #FFFFFF);
                padding: 20px;
                animation: fadeIn 2s;
            }
            ul { list-style-type: none; padding: 0; }
            li { margin: 10px 0; }
            a {
                text-decoration: none;
                color: #1E90FF;
                font-weight: bold;
                transition: all 0.3s;
            }
            a:hover {
                color: #FF4500;
                text-decoration: underline;
                transform: scale(1.1);
            }
            h1 { color: #2F4F4F; }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
        </style>
    </head>
    <body>
        <h1>Welcome to My Flask App!</h1>
        <p>Explore the available features:</p>
        <ul>
            <li><a href="/api/jackson">Personal Data (JSON)</a></li>
            <li><a href="/html/jackson">Personal Data (HTML)</a></li>
            <li><a href="/html/schedule">Class Schedule Countdown</a></li>
        </ul>
    </body>
    </html>
    """

# ========================
# Personal Data API
# ========================
@app.route('/api/jackson')
def get_jackson():
    InfoDb = [
        {
            "FirstName": "Jackson",
            "LastName": "Patrick",
            "DOB": "May 12",
            "Residence": "San Diego",
            "Email": "patwick.jackson@gmail.com",
            "Favorite_Food": ["Ramen"],
            "Hobbies": ["Sports"]
        },
        {
            "FirstName": "Arush",
            "LastName": "Shah",
            "DOB": "December 20",
            "Residence": "San Diego",
            "Email": "emailarushshah@gmail.com",
            "Favorite_Food": ["Vodka Pasta"],
            "Hobbies": ["Art", "Guitar"]
        },
        {
            "FirstName": "Marie",
            "LastName": "Curie",
            "DOB": "November 7, 1867",
            "Residence": "Paris, France",
            "Email": "marie.curie@radium.org",
            "Favorite_Food": ["Quiche"],
            "Hobbies": ["Research", "Teaching"]
        },
        {
            "FirstName": "Leonardo",
            "LastName": "Da Vinci",
            "DOB": "April 15, 1452",
            "Residence": "Amboise, France",
            "Email": "leonardo.davinci@renaissance.com",
            "Favorite_Food": ["Vegetables"],
            "Hobbies": ["Painting", "Inventing"]
        }
    ]
    return jsonify(InfoDb)

# ========================
# Personal Data HTML
# ========================
@app.route('/html/jackson')
def render_jackson_html():
    InfoDb = [
        {
            "FirstName": "Jackson",
            "LastName": "Patrick",
            "DOB": "May 12",
            "Residence": "San Diego",
            "Email": "patwick.jackson@gmail.com",
            "Favorite_Food": ["Ramen"],
            "Hobbies": ["Sports"]
        },
        {
            "FirstName": "Arush",
            "LastName": "Shah",
            "DOB": "December 20",
            "Residence": "San Diego",
            "Email": "emailarushshah@gmail.com",
            "Favorite_Food": ["Vodka Pasta"],
            "Hobbies": ["Art", "Guitar"]
        },
        {
            "FirstName": "Marie",
            "LastName": "Curie",
            "DOB": "November 7, 1867",
            "Residence": "Paris, France",
            "Email": "marie.curie@radium.org",
            "Favorite_Food": ["Quiche"],
            "Hobbies": ["Research", "Teaching"]
        },
        {
            "FirstName": "Leonardo",
            "LastName": "Da Vinci",
            "DOB": "April 15, 1452",
            "Residence": "Amboise, France",
            "Email": "leonardo.davinci@renaissance.com",
            "Favorite_Food": ["Vegetables"],
            "Hobbies": ["Painting", "Inventing"]
        }
    ]
    template = """
    <html>
    <head>
        <title>Personal Data</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                background: #FFFBF0;
                animation: fadeIn 2s;
            }
            table {
                margin: auto;
                border-collapse: collapse;
                width: 80%;
                background: #FFF;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s;
            }
            table:hover {
                transform: scale(1.02);
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
                transition: background-color 0.3s;
            }
            tr:hover {
                background: linear-gradient(to right, #FFD700, #FF4500);
                color: white;
            }
            th {
                background-color: #f2f2f2;
                color: #333;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
        </style>
    </head>
    <body>
        <h1>Personal Data</h1>
        <table>
            <thead>
                <tr>
                    <th>First Name</th>
                    <th>Last Name</th>
                    <th>DOB</th>
                    <th>Residence</th>
                    <th>Email</th>
                    <th>Hobbies</th>
                </tr>
            </thead>
            <tbody>
                {% for person in data %}
                <tr>
                    <td>{{ person.FirstName }}</td>
                    <td>{{ person.LastName }}</td>
                    <td>{{ person.DOB }}</td>
                    <td>{{ person.Residence }}</td>
                    <td>{{ person.Email }}</td>
                    <td>{{ person.Hobbies | join(', ') }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """
    return render_template_string(template, data=InfoDb)

# ========================
# Class Schedule Countdown
# ========================
@app.route('/html/schedule')
def render_schedule_html():
    now = datetime.now().time()
    current_period = None
    next_period = None

    for period in schedule:
        start = datetime.strptime(period["Start"], "%H:%M").time()
        end = datetime.strptime(period["End"], "%H:%M").time()
        if start <= now <= end:
            current_period = period
        elif now < start and not next_period:
            next_period = period

    next_day_time = get_next_school_day_start()
    template = """
    <html>
    <head>
        <title>Class Schedule Countdown</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                background: linear-gradient(to bottom, #FFF5E1, #FFDAB9);
                animation: fadeIn 2s;
            }
            h1 { font-size: 36px; color: #FF4500; }
            canvas {
                display: block;
                margin: 20px auto;
                background: #000;
                border: 2px solid #FFF;
            }
            .celebration {
                color: #FF4500;
                font-size: 24px;
                font-weight: bold;
                margin-top: 20px;
                animation: pulse 1s infinite alternate;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes pulse {
                from { transform: scale(1); }
                to { transform: scale(1.1); }
            }
        </style>
        <script>
            function startFireworks() {
                const canvas = document.getElementById("fireworksCanvas");
                const ctx = canvas.getContext("2d");
                const particles = [];
                const colors = ["#FF4500", "#FFD700", "#87CEEB", "#32CD32", "#FF69B4"];

                function Particle(x, y, color) {
                    this.x = x;
                    this.y = y;
                    this.color = color;
                    this.radius = Math.random() * 2 + 1;
                    this.dx = (Math.random() - 0.5) * 8;
                    this.dy = (Math.random() - 0.5) * 8;
                    this.life = 100;
                }

                Particle.prototype.draw = function () {
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                    ctx.fillStyle = this.color;
                    ctx.fill();
                };

                Particle.prototype.update = function () {
                    this.x += this.dx;
                    this.y += this.dy;
                    this.life -= 2;
                };

                function createFirework() {
                    const x = Math.random() * canvas.width;
                    const y = Math.random() * canvas.height;
                    const color = colors[Math.floor(Math.random() * colors.length)];
                    for (let i = 0; i < 30; i++) {
                        particles.push(new Particle(x, y, color));
                    }
                }

                function animate() {
                    ctx.fillStyle = "rgba(0, 0, 0, 0.1)";
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    particles.forEach((p, index) => {
                        if (p.life > 0) {
                            p.update();
                            p.draw();
                        } else {
                            particles.splice(index, 1);
                        }
                    });
                    requestAnimationFrame(animate);
                }

                setInterval(createFirework, 500);
                animate();
            }
        </script>
    </head>
    <body>
        <h1>Class Schedule Countdown</h1>
        {% if current_period %}
        <h2>Current Period: {{ current_period["Class"] }}</h2>
        <p>Class ends at: {{ current_period["End"] }}</p>
        {% elif next_period %}
        <h2>Next Period: {{ next_period["Class"] }}</h2>
        <p>Starts at: {{ next_period["Start"] }}</p>
        {% else %}
        <h2 class="celebration">You're done for the day! 🎉</h2>
        <canvas id="fireworksCanvas" width="400" height="400"></canvas>
        <p>Next school day starts in: {{ next_day_time }}</p>
        <script>startFireworks();</script>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(template, current_period=current_period, next_period=next_period, next_day_time=next_day_time)

if __name__ == '__main__':
    app.run(port=5009)


# Instructions to Run and Access
# ===============================
# To run the server:
# 1. Save this code in a file named flask_app.py.
# 2. Open your terminal and navigate to the directory containing flask_app.py.
# 3. Install dependencies using the following commands:
#    python -m venv venv
#    source venv/bin/activate
#    pip install -r requirements.txt
# 4. Run the server with: python flask_app.py
#
# Access the following URLs in your browser:
# ------------------------------------------
# Home Page: http://127.0.0.1:5009/
# Personal Data (JSON): http://127.0.0.1:5009/api/jackson
# Personal Data (HTML): http://127.0.0.1:5009/html/jackson
# School Schedule Countdown (HTML): http://127.0.0.1:5009/html/schedule
#
# To stop the server:
# -------------------
# Press Ctrl+C in the terminal where the server is running.

# Resolving Port Issues
# =====================
# 1. Find the process ID (PID) of the application using the port:
#    Run in terminal: lsof -i :5009
#
# 2. Kill the process using the PID:
#    Run in terminal: kill -9 <PID>
#    (Replace <PID> with the process ID returned from the lsof command.)
#
# 3. Verify the port is free:
#    Run in terminal: lsof -i :5009
#    If no output is returned, the port is now free to use.
#
# 4. If you prefer to use a different port, update the code:
#    Change app.run(port=5009) to another port, e.g., app.run(port=5010).

