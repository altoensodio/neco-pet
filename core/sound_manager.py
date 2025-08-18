import os
from pygame import mixer
from random import choice

class SoundManager:
    def __init__(self):
        mixer.init()
        self.sound_objects = {}
        self.load_sounds()

    def get_sound_objects(self):
        return self.sound_objects

    def load_sounds(self):
        sounds = [
            "bukkorosu", "buru_nyuu", "hayai_na", "ima_doko", "ima_hima",
            "muda_muda", "ngya", "shinbun", "shinu_ka", "shya", "unn", "yanya_jyan"
        ]
        for sound in sounds:
            path = os.path.join("sound", f"{sound}.mp3")
            if os.path.exists(path):
                self.sound_objects[sound] = mixer.Sound(path)

        if "ima_doko" in self.sound_objects:
            vol = 0.25
            self.sound_objects["ima_doko"].set_volume(vol)
            for s in sounds:
                if s != "ima_doko" and s in self.sound_objects:
                    self.sound_objects[s].set_volume(vol)
    
    def play_random_sound(self):
        sounds = list(self.sound_objects.values())
        if sounds:
            try:
                choice(sounds).play()
            except Exception as e:
                print("Error while trying to play sound: {e}")
