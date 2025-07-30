import requests


openWeatherMapAPIKey = "c978c0732a3d3e0b91f6a62b22c7cc27"

def get_weather(place_name):

    if not openWeatherMapAPIKey:
        return "Weather data: API key not configured"
        
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": place_name,
        "appid": openWeatherMapAPIKey,
        "units": "metric"
    }
    
    try:
        response = requests.get(url, params=params, headers={"User-Agent": "simplegeomap-app"}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            return f"Weather: {description}, {temp}°C"
        else:
            return "Weather data: Not available"
    except Exception as e:
        return "Weather data: Error fetching"