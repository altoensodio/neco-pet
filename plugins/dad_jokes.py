import asyncio, requests, aiohttp, gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib

def joke(pet, window):
    if window.loop:
        asyncio.run_coroutine_threadsafe(fetch_joke_async(window), window.loop)
    else:
        print("No loop")

async def fetch_joke_async(window):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://icanhazdadjoke.com/", headers={"Accept": "text/plain"}) as resp:
                if resp.status == 200:
                    joke = await resp.text()
                    print(joke.strip())
                    GLib.idle_add(window.show_dialogue_bubble, joke.strip(), 10)
                    window.play_random_sound()
                else:
                    print( f"Failed to fetch joke: {resp.status}")
                    GLib.idle_add(window.show_dialogue_bubble, f"Failed to fetch joke: {resp.status}", 10)
    except Exception as e:
        print(f"Error: {str(e)}")
        GLib.idle_add(window.show_dialogue_bubble, f"Error: {str(e)}", 10)

plugin = {
    "label": "Dad joke",
    "callback": joke
}
