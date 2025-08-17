import sys
from os.path import join
from tkinter import simpledialog
from gi.repository import GdkPixbuf

from gi.repository import Gtk

def ask_string_gtk(parent, title, message):
    dialog = Gtk.Dialog(title, parent, Gtk.DialogFlags.MODAL,
                        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OK, Gtk.ResponseType.OK))

    dialog.set_default_size(300, 100)
    box = dialog.get_content_area()
    label = Gtk.Label(label=message)
    entry = Gtk.Entry()
    box.add(label)
    box.add(entry)
    label.show()
    entry.show()

    response = dialog.run()
    text = None
    if response == Gtk.ResponseType.OK:
        text = entry.get_text()
    dialog.destroy()
    return text

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

class PetState:
    def __init__(self, json_obj, impath):
        self.name = json_obj['state_name']
        file_path = join(impath, json_obj['file_name'])
        # Load GIF as animation
        self.frames = GdkPixbuf.PixbufAnimation.new_from_file(file_path)
        self.ox, self.oy, self.w, self.h = json_obj['dims']
        if 'move' in json_obj:
            self.dx, self.dy = json_obj['move']
        else:
            self.dx, self.dy = 0, 0
        self.next_states = WeightedRandomMap(json_obj['transitions_to'])

class Pet:
    def __init__(self, states, window):
        self.states = states
        self.window = window
        self.current_state = list(states.values())[0]
        self.animation_iter = None
        self.x, self.y = 45, 700
        self.reset_animation()

    def reset_animation(self):
        # Create animation iterator for current state's animation
        self.animation_iter = self.current_state.frames.get_iter(None)

    def next_frame(self):
        pixbuf = self.animation_iter.get_pixbuf()
        try:
            has_next = self.animation_iter.advance(None)
        except StopIteration:
            has_next = False

        # Move position
        self.x += self.current_state.dx
        self.y += self.current_state.dy
        return pixbuf

    def __state_change(self):
        next_state_name = self.current_state.next_states.get_rand()
        self.set_state(next_state_name)

    def set_state(self, name: str):
        self.current_state = self.states[name]
        self.reset_animation()
