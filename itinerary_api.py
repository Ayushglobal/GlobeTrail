import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route('/generate-itinerary', methods=['POST'])
def generate_itinerary():
    try:
        data = request.json
        user_input = data.get('input', '')
        
        prompt = f"""As a smart AI travel planner, create a detailed response with:
        1. 3 suggested destinations (mark with ##)
        2. A 3-day itinerary for the top recommendation (mark with ###)
        3. Packing checklist (mark with ####)
        4. Budget estimates in INR (mark with #####)
        
        User request: "{user_input}"
        """
        
        response = model.generate_content(prompt)
        return jsonify({
            'status': 'success',
            'data': format_response(response.text)
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def format_response(text):
    # Convert markdown-style headers to HTML
    text = text.replace('## ', '<h3 class="text-xl font-bold mt-6 mb-3">').replace('\n##', '</h3>')
    text = text.replace('### ', '<h4 class="text-lg font-semibold mt-4 mb-2">').replace('\n###', '</h4>')
    text = text.replace('#### ', '<h5 class="font-medium mt-3 mb-1">').replace('\n####', '</h5>')
    text = text.replace('##### ', '<p class="text-blue-600 dark:text-blue-400 mt-2">').replace('\n#####', '</p>')
    return text.replace('\n', '<br>')

if __name__ == '__main__':
    app.run(port=5000, debug=True)