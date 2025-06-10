import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

# Gemini API setup
GEMINI_API_KEY = "AIzaSyB1HGZdMkukL0jqqdJa8rWCbQ5eBqU7b7E"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize DB
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 1. Signup route
@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()

    if user:
        conn.close()
        return redirect('/login?message=Account already exists. Please log in.')

    c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
    conn.commit()
    conn.close()

    session['user'] = email
    return redirect('/itinerary')

# 2. Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = email
            return redirect('/itinerary')
        else:
            return redirect('/login?message=Invalid credentials. Please try again.')

    return render_template('login.html')

# 3. Itinerary route
@app.route('/itinerary')
def itinerary():
    if 'user' in session:
        return render_template('itinerary.html')
    return redirect('/login')

# 4. Signup form page (HTML already styled)
@app.route('/signup-form')
def signup_form():
    return render_template('signup.html')

# 5. Home
@app.route('/')
def home():
    return render_template('index.html')

# 6. Generate itinerary (AI)
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
        formatted = format_response(response.text)

        return jsonify({'status': 'success', 'data': formatted})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def format_response(text):
    text = text.replace('## ', '<h3 class="text-xl font-bold mt-6 mb-3">').replace('\n##', '</h3>')
    text = text.replace('### ', '<h4 class="text-lg font-semibold mt-4 mb-2">').replace('\n###', '</h4>')
    text = text.replace('#### ', '<h5 class="font-medium mt-3 mb-1">').replace('\n####', '</h5>')
    text = text.replace('##### ', '<p class="text-blue-600 dark:text-blue-400 mt-2">').replace('\n#####', '</p>')
    return text.replace('\n', '<br>')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
