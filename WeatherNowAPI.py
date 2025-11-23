from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "b3346d809378536ca9766fd661b3bc06"

# ✅ Single City Weather (for Android app)
@app.route("/weather", methods=["GET"])
def get_weather():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City name is required"}), 400

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    r = requests.get(url)
    data = r.json()

    if data.get("cod") == 200:
        return jsonify({
            "city": city,
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["main"]
        })
    else:
        return jsonify({"error": data.get("message", "City not found")}), 404


# ✅ Multiple Cities Weather
@app.route("/weather/cities", methods=["GET"])
def get_multiple_cities_weather():
    # Example: /weather/cities?names=Muscat,Doha,Karachi
    city_names = request.args.get("names")
    if not city_names:
        return jsonify({"error": "Please provide city names like ?names=Muscat,Doha"}), 400

    cities = [name.strip() for name in city_names.split(",")]
    results = []

    for city in cities:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url).json()
        if response.get("cod") == 200:
            results.append({
                "city": city,
                "temperature": response["main"]["temp"],
                "humidity": response["main"]["humidity"],
                "condition": response["weather"][0]["main"]
            })
        else:
            results.append({"city": city, "error": response.get("message", "Not found")})

    return jsonify(results)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
