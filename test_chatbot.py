# Tests the chatbot to make sure it works
import pytest
from main import app  # Gets the Flask app from main.py

# Checks if asking for weather in Oxford works
def test_weather_response():
    with app.test_client() as client:  # Pretends to be a user
        response = client.post("/chat", json={"message": "weather in Oxford"})  # Sends a message
        assert response.status_code == 200  # Makes sure it’s successful
        data = response.get_json()
        assert "Oxford" in data["response"]  # Checks if Oxford is in the reply

# Checks if sending nothing gets an error message
def test_empty_message():
    with app.test_client() as client:
        response = client.post("/chat", json={"message": ""})
        assert response.status_code == 200
        data = response.get_json()
        assert "Please say something" in data["response"]  # Checks for the right error

# Checks if asking for forecast without a city fails
def test_forecast_no_city():
    with app.test_client() as client:
        response = client.post("/chat", json={"message": "forecast"})
        assert response.status_code == 200
        data = response.get_json()
        assert "Please mention a city" in data["response"]  # Checks for city prompt