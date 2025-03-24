import requests  # For getting data from the weather API
import traceback  # Helps find errors if something breaks
from flask import Flask, render_template, request, jsonify, session  # Tools for building the web app
from chatterbot import ChatBot  # Makes the chatbot talk
from chatterbot.trainers import ListTrainer  # Teaches the chatbot what to say
import os  # Used to make a random key
from accessories import LOCATIONS, API_KEY, get_weather  # My list of places and weather function

app = Flask(__name__)  # Starts the Flask app
app.secret_key = os.urandom(24)

# Tips for users to know what they can ask
INSTRUCTIONS = (
    "\nTry these:\n"
    "- 'Weather in [city]' (e.g., 'Weather in Oxford')\n"
    "- 'Forecast' for a 5-day forecast\n"
    "- 'What’s fun in [city]?' for travel ideas\n"
    "- 'Tell me a joke' for a laugh\n"
    "Which city should we start with?"
)

# Welcome message with tips to get started
INITIAL_MESSAGE = (
    "Hi! I’ve got weather for UK cities like Oxford, Bristol, and more." + INSTRUCTIONS
)

# Sets up the chatbot and teaches it some replies
chatbot = ChatBot("GoTravelBot", read_only=False)  # Creates the chatbot, can still add training
trainer = ListTrainer(chatbot)
travel_conversations = [
    ["Hi", INITIAL_MESSAGE],
    ["Hello", INITIAL_MESSAGE],
    ["How are you?", "I’m great, thanks! How about you—planning a trip somewhere?"],
    ["What’s fun in Oxford?", "Oxford’s got cool history—think colleges and punting! Want the weather for your visit?"],
    ["What’s fun in Bristol?", "Bristol’s got street art and bridges! Should I check the weather there?"],
    ["What’s fun in Cumbria?", "Cumbria’s perfect for hikes and lakes! Need the forecast?"],
    ["Thanks", "You’re welcome! Anything else—weather, forecast, or a joke?"],
    ["Thank you", "My pleasure! What’s next—travel plans or a quick laugh?"],
    ["Tell me a joke", "Why don’t clouds date? They’re too busy raining on everyone’s parade!"],
    ["Another joke", "What’s a tornado’s favorite game? Twister!"],
    ["Yes", "Cool! Did you want the forecast, weather, or something fun like a joke?"],
    ["Oxford", "Did you mean the weather in Oxford? Just say 'weather in Oxford' to check!"],
    ["What’s the best time to visit Oxford?", "I can’t pick dates, but I can give you the weather to plan—want it?"],
    ["What’s your name?", "I’m GoTravelBot, your travel and weather pal! How can I help?"]
]
for conversation in travel_conversations:
    trainer.train(conversation)  # Adds these replies to the chatbot
chatbot.read_only = True

# Gets 5-day weather forecast for a city
def get_forecast_data(city):
    try:
        lat, lon = LOCATIONS[city]  # Finds the city’s location
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
        response = requests.get(forecast_url, params=params)

        if response.status_code != 200:  # Checks if the API call worked
            return {"error": f"API error: {response.status_code}"}

        data = response.json()
        forecast_data = []
        processed_dates = set()  # Keeps track of days so no repeats

        for item in data.get("list", []):
            forecast_date = item["dt_txt"].split()[0]  # Gets just the date
            if forecast_date not in processed_dates and len(forecast_data) < 5:  # Only takes 5 days
                processed_dates.add(forecast_date)
                forecast_data.append({
                    "date": forecast_date,
                    "temp": round(item["main"]["temp"]),
                    "description": item["weather"][0]["description"].capitalize(),
                    "icon": item["weather"][0]["icon"]
                })
        return forecast_data
    except Exception as e:
        return {"error": str(e)}

# Looks for a city name in what the user typed
def find_city_in_message(message):
    message = message.lower()  # Makes it easier to match
    for city in LOCATIONS.keys():
        if city.lower() in message:
            return city
    return None

# Makes a nice weather reply for the user
def generate_weather_response(city, weather_info):
    return f"In {city}, it’s currently {weather_info['temperature']} with {weather_info['description'].lower()}. Humidity’s at {weather_info['humidity']}. Want the forecast too?"

# Loads the main webpage
@app.route('/')
def index():
    return render_template("index.html")

# Sends the list of cities to the webpage
@app.route('/locations')
def get_locations():
    return jsonify(LOCATIONS)

# Gives forecast data when asked
@app.route('/forecast')
def forecast():
    city = request.args.get("city")  # Gets city from the request
    if not city or city not in LOCATIONS:
        return jsonify({"error": "Invalid or missing city"}), 400
    forecast_data = get_forecast_data(city)
    return jsonify(forecast_data)

# Handles what users type into the chat
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "").strip().lower()  # Cleans up what they typed
        if not user_message:  # If they didn’t type anything
            return jsonify({"response": "Please say something!"})

        last_city = session.get("last_city")  # Remembers the last city they asked about
        weather_keywords = ['weather', 'temperature', 'climate']  # Words that mean they want weather

        # If they’re asking for weather
        if any(keyword in user_message for keyword in weather_keywords):
            city_name = find_city_in_message(user_message) or last_city  # Finds a city or uses the last one
            if not city_name:  # If no city is found
                if user_message == "weather":  # Just “weather” shows a list
                    return jsonify({
                        "response": "Which city’s weather? Pick one below:",
                        "city_suggestions": list(LOCATIONS.keys())
                    })
                return jsonify({
                    "response": "Which city's weather would you like? Try: " +
                                ", ".join(sorted(LOCATIONS.keys()))
                })

            if city_name in LOCATIONS:  # If it’s a city I know
                lat, lon = LOCATIONS[city_name]
                weather_info = get_weather(lat, lon)  # Gets the weather
                if "error" in weather_info:
                    return jsonify({
                        "response": f"Sorry, couldn’t get weather for {city_name}: {weather_info['error']}"
                    })

                session["last_city"] = city_name  # Saves the city for next time
                bot_response = generate_weather_response(city_name, weather_info)
                return jsonify({
                    "response": bot_response,
                    "weather": weather_info,
                    "city": city_name,
                    "coordinates": weather_info.get("coordinates", {}),
                    "show_forecast_button": True  # Adds a button for forecast
                })

        # If they want a forecast
        if "forecast" in user_message:
            city_name = last_city or find_city_in_message(user_message)
            if not city_name:
                return jsonify({"response": "Please mention a city first or ask about weather!"})
            forecast_data = get_forecast_data(city_name)
            if "error" in forecast_data:
                return jsonify({"response": f"Forecast error: {forecast_data['error']}"})
            return jsonify({
                "response": f"Here’s the 5-day forecast for {city_name}!",
                "forecast": forecast_data,
                "city": city_name
            })

        # Quick replies for some common things
        if "thanks" in user_message or "thank you" in user_message:
            return jsonify({"response": "You’re welcome! Need more travel help or a weather joke?"})
        if "joke" in user_message:
            return jsonify({"response": "Why don’t clouds date? They’re too busy raining on everyone’s parade! Want another?"})
        if user_message == "yes" and last_city:
            return jsonify({"response": f"Alright! Here’s a joke: What’s a tornado’s favorite game? Twister! Want the forecast for {last_city} too?"})
        if user_message in LOCATIONS.keys():
            return jsonify({"response": f"Did you want the weather for {user_message.capitalize()}? Say 'weather in {user_message.capitalize()}' to check!"})

        # If I don’t know what they mean, the chatbot tries
        bot_response = str(chatbot.get_response(user_message))
        if bot_response.lower() in ["i don't know", "i’m not sure"]:
            return jsonify({"response": INSTRUCTIONS})  # Gives tips if the chatbot’s stuck
        return jsonify({"response": bot_response})

    except Exception as e:
        print(f"Error in /chat: {traceback.format_exc()}")  # Shows errors for fixing later
        return jsonify({"response": "Something went wrong. Try again?"}), 500

# Starts the app if this file is run
if __name__ == "__main__":
    app.run(debug=True)