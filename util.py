import openai
import os
import platform
import pyttsx3
import subprocess
import random
import threading
from gtts import gTTS
from dotenv import load_dotenv


def normalize(list):
    mag = sum(list)
    return [v / mag for v in list]


def make_cum(list):
    acc = 0
    for i in range(len(list)):
        temp = list[i]
        list[i] = acc
        acc += temp
    return list


class WeightedRandomMap:
    def __init__(self, list):
        self.names = [obj["name"] for obj in list]
        self.P = make_cum(normalize([obj["probability"] for obj in list]))
        assert len(self.names) == len(self.P)

    def get_rand(self):
        val = random.random()
        for i, p in enumerate(self.P):
            if p > val:
                return self.names[i - 1]
        return self.names[-1]


def openai_query(message):
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        response = openai.Completion.create(model="text-davinci-003", prompt=message, temperature=.95, max_tokens=2500)
        return response["choices"][0]["text"]
    except Exception:
        message = "Open AI is not reachable nyaa! You might need to store your API key as an environment variable nyaa."
        return message


def speak(message, callback):
    if platform.system() == "Darwin":
        tts = gTTS(text=message)
        output_filename = "output.mp3"
        tts.save(output_filename)

        def f():
            subprocess.run(["afplay", "-r", "1", output_filename])
            os.remove(output_filename)
            callback()

        threading.Thread(target=f).start()

    else:
        engine = pyttsx3.init()
        engine.setProperty("rate", 175)
        engine.say(message)

        def f():
            engine.runAndWait()
            callback()

        threading.Thread(target=f).start()
