import os
import pygame
from gi.repository import GLib

sound_path = os.path.join("sound", "bakamitai.mp3")
bakamitai_sound = None
is_playing = False
menu_item_ref = {}

# Plugin dict
plugin = {
    "label": "Sing Baka Mitai",
    "callback": lambda pet, window: toggle_bakamitai(pet),
    "menu_item_ref": menu_item_ref,
    "stop": lambda pet: stop_bakamitai(pet)
}

def play_bakamitai(pet):
    pet.set_state("dance")
    bakamitai_sound.play()

    plugin["label"] = "Stop Baka Mitai"  # update label for next context menu
    print("[Plugin] Label updated to:", plugin["label"])

    def check_playing():
        global is_playing
        if not bakamitai_sound.get_num_channels():
            pet.set_state("idle")
            plugin["label"] = "Sing Baka Mitai"
            print("[Plugin] Label updated to:", plugin["label"])
            is_playing = False
            return False
        return True

    GLib.timeout_add(500, check_playing)

def stop_bakamitai(pet):
    if not is_playing: return
    bakamitai_sound.stop()
    pet.set_state("idle")
    plugin["label"] = "Sing Baka Mitai"
    print("[Plugin] Label updated to:", plugin["label"])

def toggle_bakamitai(pet):
    global is_playing

    if is_playing:
        stop_bakamitai(pet)
        is_playing = False
    else:
        play_bakamitai(pet)
        is_playing = True

def init(pet, window):
    global bakamitai_sound
    if os.path.exists(sound_path):
        bakamitai_sound = pygame.mixer.Sound(sound_path)
        bakamitai_sound.set_volume(0.5)
    else:
        print(f"[Plugin:BakaMitai] Sound file not found: {sound_path}")
