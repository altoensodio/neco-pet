import asyncio, aiohttp, gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib

OPENWEATHER_API_KEY = "Insert api"
CITY = "example"

def weather(pet, window):
    if window.loop:
        asyncio.run_coroutine_threadsafe(fetch_weather_async(window), window.loop)
    else:
        print("No loop available for weather plugin.")

async def fetch_weather_async(window):
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": CITY,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    weather = data['weather'][0]['main']
                    desc = data['weather'][0]['description']
                    temp = data['main']['temp']
                    msg = f"Weather in {CITY}: {weather} ({desc}), {temp}°C"
                    print(msg)
                    GLib.idle_add(window.dialogue_manager.show_dialogue_bubble, msg, 10)
                    window.sound_manager.play_random_sound()
                else:
                    fail_msg = f"Failed to fetch weather: {resp.status}"
                    print(fail_msg)
                    GLib.idle_add(window.dialogue_manager.show_dialogue_bubble, fail_msg, 10)
    except Exception as e:
        err_msg = f"Error: {str(e)}"
        print(err_msg)
        GLib.idle_add(window.dialogue_manager.show_dialogue_bubble, err_msg, 10)

plugin = {
    "label": "Weather",
    "callback": weather
}