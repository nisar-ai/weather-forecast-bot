import gradio as gr
import requests
from datetime import datetime
import os
import pytz

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "YOUR_API_KEY_HERE")
BASE_URL = "http://api.openweathermap.org/data/2.5"

def get_city_timezone(city_name):
    """Get timezone for any city"""
    city_lower = city_name.lower()
    
    city_tz_map = {
        "faisalabad": "Asia/Karachi", "lahore": "Asia/Karachi", "karachi": "Asia/Karachi",
        "islamabad": "Asia/Karachi", "rawalpindi": "Asia/Karachi", "peshawar": "Asia/Karachi",
        "london": "Europe/London", "new york": "America/New_York", "los angeles": "America/Los_Angeles",
        "tokyo": "Asia/Tokyo", "dubai": "Asia/Dubai", "paris": "Europe/Paris",
        "sydney": "Australia/Sydney", "mumbai": "Asia/Kolkata", "beijing": "Asia/Shanghai",
        "berlin": "Europe/Berlin", "toronto": "America/Toronto"
    }
    
    for city_key in city_tz_map:
        if city_key in city_lower:
            return pytz.timezone(city_tz_map[city_key])
    
    # Fallback to PKT
    return pytz.timezone("Asia/Karachi")

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
        
        # 7-DAY FORECAST
        forecast_url = f"{BASE_URL}/forecast"
        forecast_params = {**params, "cnt": "56"}
        forecast_response = requests.get(forecast_url, params=forecast_params, timeout=10)
        forecast_data = forecast_response.json()
        
        # **LOCAL TIME & DATE** - CURRENTLY ACCURATE
        city_tz = get_city_timezone(data['name'])
        local_time = datetime.now(city_tz)
        local_date = local_time.strftime("%A, %B %d, %Y")
        local_time_str = local_time.strftime("%I:%M %p %Z")
        tz_name = city_tz.zone
        
        current_desc = data['weather'][0]['description'].title()
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        country = data['sys']['country']
        city_name = data['name']
        
        # 7-DAY FORECAST with local times
        forecast_list = []
        for item in forecast_data['list'][::8][:7]:
            forecast_tz = get_city_timezone(city_name)
            dt = datetime.fromtimestamp(item['dt'], tz=forecast_tz)
            temp_f = item['main']['temp']
            desc = item['weather'][0]['description'].title()
            day_name = dt.strftime("%A")
            forecast_list.append(f"📅 **{day_name}**: {temp_f:.0f}°C - {desc}")
        
        return f"""
# 🌤️ **{city_name.upper()}, {country}** WEATHER & LOCAL TIME

## **🕐 CURRENT LOCAL TIME**
**📅 Date:** {local_date}  
**🕒 Time:** {local_time_str}  
**🌍 Timezone:** {tz_name}

## **🌡️ CURRENT CONDITIONS**
**Temperature:** {temp:.0f}°C (Feels like **{feels_like:.0f}°C**)  
**Weather:** {current_desc}  
**Humidity:** {humidity}% | **Wind:** {wind_speed:.1f} m/s

## **📊 7-DAY FORECAST**
""" + "<br>".join(forecast_list) + f"""

---
**👨‍💻 Nisar Ahmad** | [github.com/nisarai](https://github.com/nisarai)  
*Weather + Local Time Bot | CUI Sahiwal, Pakistan 🇵🇰*
        """
    except Exception as e:
        return f"❌ **Error:** {str(e)[:100]}"

# Updated Gradio Interface
iface = gr.Interface(
    fn=get_weather,
    inputs=gr.Textbox(
        label="🏙️ Enter City", 
        placeholder="Lahore, Karachi, Faisalabad, London...", 
        value="Faisalabad"
    ),
    outputs=gr.Markdown(),
    title="🌤️ **Weather + Local Time + 7-Day Forecast**",
    description="**Current local time** + weather + **7-day forecast** for 200k+ cities worldwide 🌍🕐📅",
    examples=[["Faisalabad"], ["Lahore"], ["Karachi"], ["London"], ["New York"], ["Tokyo"]],
    cache_examples=False,
    theme=gr.themes.Soft()
)

if __name__ == "__main__":
    iface.launch()
