import gradio as gr
import requests
from datetime import datetime
import os

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "YOUR_API_KEY_HERE")
BASE_URL = "http://api.openweathermap.org/data/2.5"

def get_weather(city):
    if not WEATHER_API_KEY or len(WEATHER_API_KEY) != 32:
        return "❌ **API Key Required**. Add `WEATHER_API_KEY` in HF Spaces Secrets."
    
    try:
        url = f"{BASE_URL}/weather"
        params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code != 200:
            params["q"] = f"{city}, Pakistan"
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code != 200:
                return f"❌ **'{city}' not found**. Try: Lahore, Karachi, Faisalabad, London"
        
        forecast_url = f"{BASE_URL}/forecast"
        forecast_params = {**params, "cnt": "56"}
        forecast_response = requests.get(forecast_url, params=forecast_params, timeout=10)
        forecast_data = forecast_response.json()
        
        current_desc = data['weather'][0]['description'].title()
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        country = data['sys']['country']
        city_name = data['name']
        
        forecast_list = []
        for item in forecast_data['list'][::8][:7]:
            dt = datetime.fromtimestamp(item['dt'])
            temp_f = item['main']['temp']
            desc = item['weather'][0]['description'].title()
            forecast_list.append(f"📅 **{dt.strftime('%A')}**: {temp_f:.0f}°C - {desc}")
        
        return f"""
# 🌤️ **{city_name.upper()}, {country}** WEATHER

## **🌡️ CURRENT CONDITIONS**
**Temperature:** {temp:.0f}°C (Feels like **{feels_like:.0f}°C**)  
**Weather:** {current_desc}  
**Humidity:** {humidity}% | **Wind:** {wind_speed:.1f} m/s

## **📊 7-DAY FORECAST**
""" + "<br>".join(forecast_list) + f"""

---
**👨‍💻 Nisar Ahmad** | [github.com/nisarai](https://github.com/nisarai)
        """
    except Exception as e:
        return f"❌ **Error:** {str(e)[:100]}"

iface = gr.Interface(
    fn=get_weather,
    inputs=gr.Textbox(label="🏙️ Enter City", placeholder="Lahore, Karachi, London...", value="Lahore"),
    outputs=gr.Markdown(),
    title="🌤️ Weather Forecast Bot",
    description="Current weather + 7-day forecast for 200k+ cities worldwide",
    examples=[["Lahore"], ["Karachi"], ["London"], ["New York"]],
    cache_examples=False
)

if __name__ == "__main__":
    iface.launch()
