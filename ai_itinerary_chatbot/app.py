from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from utils import generate_itinerary_gemini

app = Flask(__name__, template_folder='Templates') 
CORS(app)

@app.route('/')
def home():
    return render_template("itinerary.html")  

@app.route('/generate-itinerary', methods=['POST'])
def generate_itinerary():
    try:
        data = request.get_json()
        destination = data.get('destination')
        days = data.get('days', 2)
        people = data.get('people', 'solo')
        interests = data.get('interests', 'sightseeing and nature')
        budget = data.get('budget', 'medium')

        if not destination:
            return jsonify({'status': 'error', 'message': 'Destination is required'}), 400

        result = generate_itinerary_gemini(destination, days, people, interests, budget)
        return jsonify({'status': 'success', 'data': result})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
