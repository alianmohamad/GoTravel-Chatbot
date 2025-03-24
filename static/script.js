document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");  // Where chat messages show up
    const userInput = document.getElementById("user-input");  // Box for typing messages
    const sendBtn = document.getElementById("send-btn");  // Button to send messages
    const mapContainer = document.getElementById("map");  // Space for the map
    const weatherInfo = document.getElementById("weather-info");  // Shows weather details
    const selectedCity = document.getElementById("selected-city");  // Shows the city name
    const forecastDiv = document.getElementById("forecast");  // Shows the 5-day forecast

    let map = null;  // Holds the map object

    // Sets up the map with all England cities
    function initDefaultMap() {
        map = L.map(mapContainer).setView([52.3555, -1.1743], 6); // Centers on England
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "© OpenStreetMap contributors"  // Credits for the map
        }).addTo(map);

        fetch("/locations")  // Gets city locations from the server
            .then(response => response.json())
            .then(locations => {
                Object.entries(locations).forEach(([city, coords]) => {
                    L.marker([coords[0], coords[1]]).addTo(map)  // Adds a marker for each city
                        .bindPopup(city);  // Shows city name when clicked
                });
            })
            .catch(error => console.error("Error loading locations:", error));
    }

    // Puts placeholders in weather and forecast at the start
    function setDefaultUI() {
        selectedCity.textContent = "England Weather";  // Default city title
        weatherInfo.innerHTML = `
            <p>Temperature: <strong>-</strong></p>
            <p>Description: <strong>-</strong></p>
            <p>Humidity: <strong>-</strong></p>
            <img src="http://openweathermap.org/img/wn/01d.png" alt="Placeholder icon" >
        `;

        resetForecastToPlaceholders();  // Clears forecast to start fresh
        addMessage("Hi! I’ve got weather for England cities like Oxford, Bristol, and more." +
            "\nTry these:\n" +
            "- 'Weather in [city]' (e.g., 'Weather in Oxford')\n" +
            "- 'Forecast' for a 5-day forecast\n" +
            "- 'What’s fun in [city]?' for travel ideas\n" +
            "- 'Tell me a joke' for a laugh\n" +
            "Which city should we start with?", false);  // Welcome message
    }

    // Clears forecast and adds blank days
    function resetForecastToPlaceholders() {
        forecastDiv.innerHTML = "";  // Empties the forecast box
        for (let i = 0; i < 5; i++) {
            const forecastItem = document.createElement("div");
            forecastItem.classList.add("forecast-item");
            forecastItem.innerHTML = `
                <strong>-</strong><br>
                <img src="http://openweathermap.org/img/wn/01d.png" alt="Placeholder icon">
                <p>-</p>
                <p>-</p>
            `;
            forecastDiv.appendChild(forecastItem);  // Adds 5 empty days
        }
    }

    // Gets forecast data from the server
    function fetchForecast(city) {
        console.log("Fetching forecast for:", city);  // For debugging
        fetch(`/forecast?city=${encodeURIComponent(city)}`)
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => { throw new Error(`Status: ${response.status}, ${text}`); });
                }
                return response.json();
            })
            .then(data => {
                forecastDiv.innerHTML = "";  // Clears old forecast
                if (data.error) {
                    forecastDiv.innerHTML = `<p>Error: ${data.error}</p>`;
                    return;
                }
                if (!Array.isArray(data) || data.length === 0) {
                    forecastDiv.innerHTML = `<p>No forecast data available</p>`;
                    return;
                }
                data.forEach(day => {  // Adds each day to the forecast
                    const forecastItem = document.createElement("div");
                    forecastItem.classList.add("forecast-item");
                    const formattedDate = new Date(day.date).toLocaleDateString('en-US', {
                        weekday: 'short', month: 'short', day: 'numeric'
                    });
                    forecastItem.innerHTML = `
                        <strong>${formattedDate}</strong><br>
                        <img src="http://openweathermap.org/img/wn/${day.icon}.png" alt="Weather icon">
                        <p>${day.temp}°C</p>
                        <p>${day.description}</p>
                    `;
                    forecastDiv.appendChild(forecastItem);
                });
            })
            .catch(error => {
                forecastDiv.innerHTML = `<p>Error loading forecast: ${error.message}</p>`;
            });
    }

    // Moves the map to a new city
    function updateMap(lat, lon) {
        if (map) {
            map.setView([lat, lon], 10); // Zooms to the city
        }
    }

    // Updates the weather info on the page
    function updateWeatherUI(city, weather, coords) {
        selectedCity.textContent = city;
        weatherInfo.innerHTML = `
            <p>Temperature: <strong>${weather.temperature}</strong></p>
            <p>Description: <strong>${weather.description}</strong></p>
            <p>Humidity: <strong>${weather.humidity}</strong></p>
            <img src="${weather.icon}" alt="Weather icon">
        `;
        updateMap(coords.lat, coords.lon);  // Moves map to the city
    }

    // Updates the forecast with new data
    function updateForecastUI(city) {
        fetchForecast(city);
    }

    // Adds a message to the chat box
    function addMessage(text, isUser) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("chat-message", isUser ? "user-message" : "bot-message");  // Styles it as user or bot
        msgDiv.textContent = text;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;  // Scrolls to the bottom
    }

    // Shows a list of cities to click
    function addCitySuggestions(text, cities) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("chat-message", "bot-message");
        msgDiv.textContent = text;

        const cityList = document.createElement("div");
        cityList.className = "city-suggestions";
        cities.forEach(city => {
            const cityBtn = document.createElement("button");
            cityBtn.textContent = city;
            cityBtn.className = "btn btn-sm btn-outline-primary m-1";
            cityBtn.onclick = () => {  // When clicked, asks for weather
                userInput.value = `weather in ${city}`;
                sendMessage();
            };
            cityList.appendChild(cityBtn);
        });

        msgDiv.appendChild(cityList);
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Adds a button to get the forecast
    function addForecastButton(text, city) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("chat-message", "bot-message");
        msgDiv.textContent = text;

        const forecastBtn = document.createElement("button");
        forecastBtn.textContent = "Get Forecast";
        forecastBtn.className = "btn btn-sm btn-outline-success m-1";
        forecastBtn.onclick = () => {  // When clicked, gets forecast
            userInput.value = "forecast";
            sendMessage();
        };
        msgDiv.appendChild(forecastBtn);

        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Sends the user’s message to the server
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;  // Stops if nothing’s typed

        addMessage(message, true);  // Shows user’s message
        userInput.value = "";  // Clears the input box

        fetch("/chat", {  // Sends message to the server
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            if (data.city_suggestions) {  // Shows city buttons if needed
                addCitySuggestions(data.response, data.city_suggestions);
            } else if (data.show_forecast_button) {  // Shows weather with a forecast button
                addForecastButton(data.response, data.city);
                resetForecastToPlaceholders(); // Clears old forecast
                updateWeatherUI(data.city, data.weather, data.coordinates);
            } else {
                addMessage(data.response, false);  // Shows bot’s reply
                if (data.weather) {
                    resetForecastToPlaceholders(); // Clears old forecast
                    updateWeatherUI(data.city, data.weather, data.coordinates);
                }
                if (data.forecast) {
                    updateForecastUI(data.city);
                }
            }
        })
        .catch(error => {
            addMessage("Sorry, I'm having trouble processing your request.", false);  // Shows error if it fails
        });
    }

    // Sets up the page when it loads
    initDefaultMap();
    setDefaultUI();

    // Listens for clicks or Enter to send messages
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });
});