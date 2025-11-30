import redis
import json
from flask import Flask, request, jsonify
import aiohttp
import asyncio

app = Flask(__name__)

# Connect to Redis
cache = redis.StrictRedis(host='localhost', port=6379, db=0)

API_KEY = "b3346d809378536ca9766fd661b3bc06"

# Async function to fetch weather data
async def fetch_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# ✅ Single City Weather (with caching)
@app.route("/weather", methods=["GET"])
async def get_weather():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City name is required"}), 400

    # Check if the data is already cached
    cached_data = cache.get(city)
    if cached_data:
        return jsonify(json.loads(cached_data))

    # Fetch data from OpenWeather if not cached
    data = await fetch_weather_data(city)

    if data.get("cod") == 200:
        # Cache the result for 5 minutes (300 seconds)
        cache.setex(city, 300, json.dumps({
            "city": city,
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["main"]
        }))
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
async def get_multiple_cities_weather():
    city_names = request.args.get("names")
    if not city_names:
        return jsonify({"error": "Please provide city names like ?names=Muscat,Doha"}), 400

    cities = [name.strip() for name in city_names.split(",")]
    results = []

    # Run all the city fetch tasks concurrently
    tasks = [fetch_weather_data(city) for city in cities]
    responses = await asyncio.gather(*tasks)

    for city, data in zip(cities, responses):
        if data.get("cod") == 200:
            results.append({
                "city": city,
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "condition": data["weather"][0]["main"]
            })
        else:
            results.append({"city": city, "error": data.get("message", "Not found")})

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

