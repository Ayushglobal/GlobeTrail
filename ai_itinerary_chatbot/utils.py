import google.generativeai as genai

# Set your Gemini API key here
GEMINI_API_KEY = "AIzaSyB1HGZdMkukL0jqqdJa8rWCbQ5eBqU7b7E"
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

def generate_itinerary_gemini(destination, days, people, interests, budget):
    prompt = f"""
Act like a smart travel planner.

Create a {days}-day detailed itinerary for a trip to {destination} for a {people} traveler(s) interested in {interests}. 
The budget is {budget} level (low/medium/high).

Each day should have 3-4 activities with proper places, food spots, local experiences, and estimated timing. 
Add travel tips, and avoid generic suggestions. Return only the day-wise plan, no greeting or ending.
"""

    response = model.generate_content(prompt)
    return response.text
