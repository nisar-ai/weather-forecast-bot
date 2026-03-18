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
        "berlin": "Europe/Berlin", "toronto": "America/Toronto", "moscow": "Europe/Moscow"
    }
    
    for city_key in city_tz_map:
        if city_key in city_lower:
            return pytz.timezone(city_tz_map[city_key])
    
    return pytz.timezone("Asia/Karachi")

def get_weather(city):
    if not WEATHER_API_KEY or len(WEATHER_API_KEY) != 32:
        return None, None, None, None, None, None, None, "❌ **API Key Required**. Add `WEATHER_API_KEY` in HF Spaces Secrets."
    
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
                return None, None, None, None, None, None, None, f"❌ **'{city}' not found**. Try: Lahore, Karachi, Faisalabad"
        
        # FORECAST DATA
        forecast_url = f"{BASE_URL}/forecast"
        forecast_params = {**params, "cnt": "56"}
        forecast_response = requests.get(forecast_url, params=forecast_params, timeout=10)
        forecast_data = forecast_response.json()
        
        # LOCAL TIME
        city_tz = get_city_timezone(data['name'])
        local_time = datetime.now(city_tz)
        local_date = local_time.strftime("%A, %B %d, %Y")
        local_time_str = local_time.strftime("%I:%M %p")
        tz_name = city_tz.zone
        
        # CURRENT CONDITIONS
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        country = data['sys']['country']
        city_name = data['name']
        sunrise = datetime.fromtimestamp(data['sys']['sunrise'], tz=city_tz).strftime("%I:%M %p")
        sunset = datetime.fromtimestamp(data['sys']['sunset'], tz=city_tz).strftime("%I:%M %p")
        
        # METRIC DISPLAYS WITH CLEAR LABELS
        temp_display = f"### 🌡️ **Temperature**\n**{temp:.0f}°C**"
        feels_display = f"### 💨 **Feels Like**\n**{feels_like:.0f}°C**"
        humidity_display = f"### 💧 **Humidity**\n**{humidity}%**"
        wind_display = f"### 💨 **Wind Speed**\n**{wind_speed:.1f} m/s**"
        
        # 7-DAY FORECAST
        forecast_list = []
        for item in forecast_data['list'][::8][:7]:
            forecast_tz = get_city_timezone(city_name)
            dt = datetime.fromtimestamp(item['dt'], tz=forecast_tz)
            temp_f = item['main']['temp']
            desc = item['weather'][0]['description'].title()
            day_name = dt.strftime("%A")[:3]
            forecast_list.append(f"**{day_name}**: {temp_f:.0f}°C - {desc[:12]}")
        
        forecast_text = "\n".join(forecast_list)
        
        return (
            f"**{city_name}, {country}** • {local_date}",
            f"🕐 **{local_time_str} ({tz_name})** • 🌅 {sunrise} | 🌇 {sunset}",
            temp_display, feels_display, humidity_display, wind_display,
            forecast_text,
            "✅ Weather loaded successfully!"
        )
        
    except Exception as e:
        return None, None, None, None, None, None, None, f"❌ **Error:** {str(e)[:100]}"

# PROFESSIONAL WEATHER DASHBOARD
css = """
.metric-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
              border-radius: 15px; padding: 25px; color: white; text-align: center; margin: 10px 5px;}
.header-card {background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
              border-radius: 20px; padding: 25px; color: white; text-align: center;}
.forecast-card {background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                border-radius: 12px; padding: 15px; margin: 5px; color: white;}
"""

with gr.Blocks(title="Weather Dashboard Pro", css=css) as demo:
    
    gr.Markdown("""
    # 🌤️ **Professional Weather Dashboard**
    **Local Time • Current Conditions • 7-Day Forecast** • 200k+ Cities Worldwide
    """)
    
    gr.Markdown("*Built by Nisar Ahmad | CUI Sahiwal, Pakistan 🇵🇰*")
    
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group():
                gr.Markdown("### 🏙️ **Search Weather**")
                city_input = gr.Textbox(
                    label="Enter City Name", 
                    placeholder="Faisalabad, Lahore, London, Tokyo...",
                    value="Faisalabad"
                )
                get_btn = gr.Button("🚀 Get Weather", variant="primary", size="lg")
        
        with gr.Column(scale=1):
            with gr.Group():
                gr.Markdown("### 📍 **Quick Cities**")
                gr.Examples(
                    examples=[["Islamabad"], ["London"], ["Dubai"], ["New York"], ["Karachi"], ["Lahore"], ["Beijing"]],
                    inputs=[city_input]
                )
    
    # LOCAL TIME & LOCATION HEADER
    with gr.Row():
        location_display = gr.Markdown("", elem_classes="header-card")
        time_display = gr.Markdown("", elem_classes="header-card")
    
    # CURRENT CONDITIONS METRICS - CLEAR LABELS
    with gr.Row():
        temp_metric = gr.Markdown("🌡️ **Temperature**\n**Loading...**", elem_classes="metric-card")
        feels_metric = gr.Markdown("💨 **Feels Like**\n**Loading...**", elem_classes="metric-card")
    
    with gr.Row():
        humidity_metric = gr.Markdown("💧 **Humidity**\n**Loading...**", elem_classes="metric-card")
        wind_metric = gr.Markdown("💨 **Wind Speed**\n**Loading...**", elem_classes="metric-card")
    
    # 7-DAY FORECAST
    gr.Markdown("### 📊 **7-Day Forecast**")
    forecast_display = gr.Markdown("**Loading forecast...**", elem_classes="forecast-card")
    
    status_display = gr.Textbox(label="Status", interactive=False)
    
    # EVENT HANDLER
    get_btn.click(
        fn=get_weather,
        inputs=[city_input],
        outputs=[location_display, time_display, 
                temp_metric, feels_metric, humidity_metric, wind_metric,
                forecast_display, status_display]
    )
    
    gr.Markdown("---")
    gr.Markdown("*Powered by OpenWeatherMap API • github.com/nisarai*")

if __name__ == "__main__":
    demo.launch(
        theme=gr.themes.Soft(),
        server_name="0.0.0.0",
        server_port=7860
    )
