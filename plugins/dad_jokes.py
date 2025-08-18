import asyncio, aiohttp, gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib

def init(pet, window):
    #add joke to random dialoges
    window.dialogue_manager.add_func_to_random_dialogues(lambda: joke(pet, window), [1,3])

def joke(pet, window):
    if window.loop:
        asyncio.run_coroutine_threadsafe(fetch_joke_async(window), window.loop)
    else:
        print("No loop available.")

async def fetch_joke_async(window):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://icanhazdadjoke.com/", headers={"Accept": "text/plain"}) as resp:
                if resp.status == 200:
                    joke = await resp.text()
                    print(joke.strip())
                    GLib.idle_add(window.dialogue_manager.show_dialogue_bubble, joke.strip(), 10)
                    window.sound_manager.play_random_sound()
                else:
                    print( f"Failed to fetch joke: {resp.status}")
                    GLib.idle_add(window.dialogue_manager.show_dialogue_bubble, f"Failed to fetch joke: {resp.status}", 10)
    except Exception as e:
        print(f"Error: {str(e)}")
        GLib.idle_add(window.dialogue_manager.dialogue_manager.show_dialogue_bubble, f"Error: {str(e)}", 10)

plugin = {
    "label": "Dad Joke",
    "callback": joke
}
