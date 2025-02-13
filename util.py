import openai
import os
import platform
import pyttsx3
import pyttsx4
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
    
    messages = [{"role": "user", "content": message}]

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini", 
            messages=messages, 
            temperature=0.75, 
            max_tokens=2500
        )
        return response.choices[0].message.content
    except Exception as e:
        #print(f"Error: {e}")
        message=""
        return message


def speak(message, callback):
    if platform.system() == "Windows":
        engine = pyttsx3.init()
        engine.setProperty("rate", 175)
        engine.say(message)

        def f():
            engine.runAndWait()
            callback()

        threading.Thread(target=f).start()

    elif platform.system() == "Darwin":
        tts = gTTS(text=message)
        output_filename = "output.mp3"
        tts.save(output_filename)

        def f():
            subprocess.run(["afplay", "-r", "1", output_filename])
            os.remove(output_filename)
            callback()

        threading.Thread(target=f).start()

    elif platform.system() == "Linux":
        engine = pyttsx4.init()
        engine.setProperty("rate", 175)
        engine.say(message)

        def f():
            engine.runAndWait()
            callback()

        threading.Thread(target=f).start()
