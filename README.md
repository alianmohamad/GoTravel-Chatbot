# GoTravel Chatbot
A Flask-based chatbot providing weather updates and forecasts for England cities with a map interface.

# Features
- Real-time current weather and 5-day forecasts for 10 UK cities
- Chatbot trained with travel-focused queries using ChatterBot
- Interactive map with Leaflet.js showing selected city
- Conversational session memory (remembers last city)
- Responsive UI with Bootstrap and custom styling

# Setup Instructions
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Add your OpenWeather API key in a file named `api_key.txt` in the root directory:
```
YOUR_API_KEY_HERE
```

3. Run the Flask app:
```bash
python main.py
```

4. Open your browser and visit:
```
http://127.0.0.1:5000/
```

## Sample Chatbot Questions
- "Hi"
- "What’s the weather like in Oxford?"
- "Forecast for Cambridge"
- "Tell me a joke"
- "Thanks"

## Technologies Used
- Python
- Flask
- ChatterBot
- OpenWeather API
- HTML/CSS/Bootstrap
- JavaScript
- Leaflet.js

## Author
**Mohamad Alian**  
Postgraduate Student, Swinburne University of Technology

