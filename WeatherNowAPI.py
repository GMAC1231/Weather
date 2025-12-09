from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ✅ Your OpenWeatherMap API key
API_KEY = "b3346d809378536ca9766fd661b3bc06"


# 🌤 Single City Weather
@app.route("/weather", methods=["GET"])
def get_weather():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City name is required"}), 400

    try:
        # Use HTTPS for secure connection
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("cod") == 200:
            return jsonify({
                "city": city,
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "condition": data["weather"][0]["main"]
            })
        else:
            return jsonify({"error": data.get("message", "City not found")}), 404

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network error: {str(e)}"}), 500


# 🌍 Multiple Cities Weather
@app.route("/weather/cities", methods=["GET"])
def get_multiple_cities_weather():
    # Example: /weather/cities?names=Muscat,Doha,Karachi
    city_names = request.args.get("names")
    if not city_names:
        return jsonify({"error": "Please provide city names like ?names=Muscat,Doha"}), 400

    cities = [name.strip() for name in city_names.split(",")]
    results = []

    for city in cities:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url, timeout=10)
            data = response.json()

            if data.get("cod") == 200:
                results.append({
                    "city": city,
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "condition": data["weather"][0]["main"]
                })
            else:
                results.append({"city": city, "error": data.get("message", "City not found")})

        except requests.exceptions.RequestException as e:
            results.append({"city": city, "error": f"Network error: {str(e)}"})

    return jsonify(results)


# 🏠 Home route (for testing on Render)
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "🌦 WeatherNow API is running successfully!",
        "endpoints": {
            "/weather?city=Muscat": "Get weather for a single city",
            "/weather/cities?names=Muscat,Doha,Karachi": "Get weather for multiple cities"
        }
    })


if __name__ == "__main__":
    # ⚙️ Run on 0.0.0.0 for Render / localhost access
    app.run(host="0.0.0.0", port=5000)
