import json
import os
import platform
import random
import subprocess
import sys
import tkinter as tk
from os.path import join
from pet import Pet, PetState
from pygame import mixer

if len(sys.argv) >= 2:
    CONFIG_PATH = sys.argv[1]
else:
    CONFIG_PATH = os.path.join("assets", "neco_arc")

# initial location
current_x = 0
current_y = 0

start_drag_x = 0
start_drag_y = 0
dragging = False


def create_event_func(event, pet):
    if event["type"] == "state_change":
        return lambda e: pet.set_state(event["new_state"])
    elif event["type"] == "chatgpt":
        return lambda e: pet.start_chat(event["prompt"], event["listen_state"], event["response_state"], event["end_state"])


def update():
    frame = pet.next_frame()
    label.configure(image=frame)
    # pause updating coordinates while dragging
    if not dragging:
        window.geometry(f'{pet.current_state.w}x{pet.current_state.h}+{current_x}+{current_y}')
    window.after(100, update)


def open_file():
    filename = "output.txt"
    if platform.system() == "Windows":
        subprocess.Popen(["notepad.exe", filename])
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", filename])
    elif platform.system() == "Linux":
        subprocess.Popen(["xdg-open", filename])


def close_window(event):
    menu = tk.Menu(window, tearoff=0)
    menu.add_command(label="output.txt", command=open_file)
    menu.add_command(label="close", command=window.destroy)
    try:
        menu.tk_popup(event.x_root, event.y_root, 0)
    finally:
        menu.grab_release()


def on_start_drag(event):
    global start_drag_x, start_drag_y, dragging
    if event.state & 0x0004:
        start_drag_x = event.x
        start_drag_y = event.y
        dragging = True
    else:
        # play random sound on click without drag
        random_sound = random.choice([bukkorosu, buru_nyuu, hayai_na, ima_doko, ima_hima,
                                      muda_muda, ngya, shinbun, shinu_ka, shya, unn, yanya_jyan])
        mixer.Sound.play(random_sound)


def on_drag(event):
    global start_drag_x, start_drag_y, dragging
    if dragging:
        x = window.winfo_x() - start_drag_x + event.x
        y = window.winfo_y() - start_drag_y + event.y
        window.geometry(f"+{x}+{y}")


def on_stop_drag(event):
    global dragging, current_x, current_y
    dragging = False
    current_x = window.winfo_x()
    current_y = window.winfo_y()


if __name__ == "__main__":
    window = tk.Tk()

    with open(join(CONFIG_PATH, "config.json")) as config:
        config_obj = json.load(config)
        states = {state['state_name']: PetState(state, CONFIG_PATH) for state in config_obj["states"]}
        for state in states.values():
            for state in state.next_states.names:
                assert state in states

        pet = Pet(states, window)

        for event in config_obj["events"]:
            event_func = create_event_func(event, pet)
            if event["trigger"] == "click":
                window.bind("<Double-Button-1>", event_func)


    # neco-configuration
    if platform.system() == "Windows":
        window.config(highlightbackground='black')
        label = tk.Label(window, bd=0, bg='black')
        window.overrideredirect(True)
        window.wm_attributes('-transparentcolor', 'black')
    elif platform.system() == "Darwin":
        label = tk.Label(window, bd=0, bg='white')
        window.overrideredirect(True)
    elif platform.system() == "Linux":
        label = tk.Label(window, bd=0, bg='white')
        window.wm_attributes('-type', 'splash')

    label.pack()

mixer.init()

bukkorosu = mixer.Sound("sound/bukkorosu.mp3")
buru_nyuu = mixer.Sound("sound/buru_nyuu.mp3")
hayai_na = mixer.Sound("sound/hayai_na.mp3")
ima_doko = mixer.Sound("sound/ima_doko.mp3")
ima_hima = mixer.Sound("sound/ima_hima.mp3")
muda_muda = mixer.Sound("sound/muda_muda.mp3")
ngya = mixer.Sound("sound/ngya.mp3")
shinbun = mixer.Sound("sound/shinbun.mp3")
shinu_ka = mixer.Sound("sound/shinu_ka.mp3")
shya = mixer.Sound("sound/shya.mp3")
unn = mixer.Sound("sound/unn.mp3")
yanya_jyan = mixer.Sound("sound/yanya_jyan.mp3")

ima_doko.set_volume(0.25)
for sound in [bukkorosu, buru_nyuu, hayai_na, ima_hima,
              muda_muda, ngya, shinbun, shinu_ka, shya, unn, yanya_jyan]:
    sound.set_volume(ima_doko.get_volume())

window.bind('<ButtonPress-1>', on_start_drag)
window.bind('<B1-Motion>', on_drag)
window.bind('<ButtonRelease-1>', on_stop_drag)
if platform.system() == "Darwin":
    window.bind('<Button-2>', close_window)
else:
    window.bind('<Button-3>', close_window)

window.after(100, update)
window.mainloop()
