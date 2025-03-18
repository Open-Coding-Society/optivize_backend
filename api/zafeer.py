from flask import Flask, jsonify
from flask_cors import CORS

# initialize a flask application (app)
app = Flask(__name__)
CORS(app, supports_credentials=True, origins='*')  # Allow all origins (*)

# add an api endpoint to flask app
@app.route('/api/zafeer', methods=['GET'])
def get_data():
    def get_id():
        return jsonify({InfoDb})
    # start a list, to be used like a information database
    InfoDb = []

    # add a row to list, an Info record
    InfoDb.append({
        "FirstName": "Zafeer",
        "LastName": "Ahmed",
        "DOB": "January 11",
        "Residence": "San Diego",
        "Email": "zafeer10ahmed@gmail.com",
    })
    
    return jsonify(InfoDb)

# add an HTML endpoint to flask app
@app.route('/')
def say_hello():
    html_content = """
    <html>
    <head>
        <title>Hello</title>
    </head>
    <body>
        <h2>Hello, World!</h2>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run(port=5001)