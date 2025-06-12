import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

# Setup Gemini API
GEMINI_API_KEY = "AIzaSyB1HGZdMkukL0jqqdJa8rWCbQ5eBqU7b7E"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

init_db()

# === Auth Routes ===
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

@app.route('/signup-form')
def signup_form():
    return render_template('signup.html')

# === Protected Itinerary Page ===
@app.route('/itinerary')
def itinerary():
    if 'user' in session:
        return render_template('itinerary.html')
    return redirect('/login')

# === Homepage ===
@app.route('/')
def home():
    return render_template('index.html')

# === Itinerary Generation ===
@app.route('/generate-itinerary', methods=['POST'])
def generate_itinerary():
    data = request.get_json()

    destination = data.get("destination", "").strip().lower()
    source = data.get("source", "").strip().lower()
    people = data.get("people", "").strip().lower()
    budget = int(data.get("budget", "0"))
    preferences = data.get("preferences", "").strip().lower()

    if not destination or not source or not people or not budget:
        return jsonify({
            "status": "error",
            "message": "Incomplete information provided"
        })

    if destination == "lonavla":
        itinerary = f"""
<b>🌄 Lonavla Itinerary (From {source.title()} | {people.title()} | ₹{budget})</b><br><br>

<b>Day 1:</b><br>
- Depart from {source.title()} early morning (by local train or cab)<br>
- Visit Bhushi Dam and enjoy monsoon views ☔<br>
- Lunch at German Bakery Wunderbar<br>
- Explore Tiger’s Leap and Rajmachi Point 🌄<br>
- Check-in to a budget-friendly homestay/hotel (₹1000-1500)<br>
- Dinner at Mapro Garden Restaurant<br><br>

<b>Day 2:</b><br>
- Breakfast at hotel<br>
- Visit Karla & Bhaja Caves (Auto from market area)<br>
- Lunch at Rama Krishna Lonavla<br>
- Relax at Lonavla Lake / do some light shopping<br>
- Return to Pune by evening 🚆<br><br>

<b>Total Cost Estimation:</b><br>
- Travel: ₹500 (train) / ₹2000 (cab)<br>
- Food: ₹800-1000<br>
- Stay: ₹1000-1500<br>
- Entry + Misc: ₹500<br><br>
✅ <b>Estimated Total:</b> ₹3000 - ₹4500 only<br><br>
<b>Tip:</b> Try chikki from Maganlal – it’s a Lonavla classic! 🍬
"""
        return jsonify({"status": "success", "data": itinerary})

    return jsonify({
        "status": "success",
        "data": "Sorry! I don’t have a detailed itinerary for that destination yet. Please try another location or refine your query."
    })

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return '', 200  # Handle CORS preflight

    try:
        data = request.get_json()
        messages = data.get("messages", [])

        if not messages:
            return jsonify({"status": "error", "message": "No messages provided."})

        # Correct format using plain dicts
        history = [
            {"role": msg["role"], "parts": [msg["content"]]}
            for msg in messages[:-1]
        ]
        last_message = messages[-1]["content"]

        chat = model.start_chat(history=history)
        response = chat.send_message(last_message)

        return jsonify({
            "status": "success",
            "reply": response.text
        })

    except Exception as e:
        print("Chat error:", str(e))
        return jsonify({
            "status": "error",
            "message": "Failed to generate response."
        })




# === Run the Flask App ===
if __name__ == '__main__':
    app.run(debug=True)
