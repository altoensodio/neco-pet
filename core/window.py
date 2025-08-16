import gi, json, os, platform, random, sys, pygame, requests, aiohttp, asyncio, threading, time
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('Gtk', '3.0')
from os.path import join
from pygame import mixer
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
from typing import Callable

from pet import Pet, PetState
from utils import reminder_utils, alarm_utils
from core.sound_manager import SoundManager
from ui.menu import create_context_menu
from ui.dialogue_bubble import DialogueBubble
from core.plugin_manager import PluginManager

class NecoArcWindow(Gtk.Window):   
    def __init__(self, config_path, loop):
        super().__init__(title="Cage")
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_app_paintable(True)
        self.loop = loop
        self.connect("delete-event", self.on_delete_event)
        self.random_dialogues = []
        self.active_reminders = []
        self.active_async_tasks = []
        self.load_reminders_from_file()
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        with open(join(config_path, "config.json")) as config_file:
            config_obj = json.load(config_file)
            self.states = {state['state_name']: PetState(state, config_path) for state in config_obj["states"]}
            for state in self.states.values():
                for next_state in state.next_states.names:
                    assert next_state in self.states
            self.pet = Pet(self.states, self)

            for event in config_obj.get("events", []):
                event_func = self.create_event_func(event, self.pet)
                if event["trigger"] == "click":
                    self.connect("button-press-event", lambda w, e, f=event_func: self._on_click_event(e, f))
        mixer.init()
        self.sound_manager = SoundManager()
        self.sound_objects = self.sound_manager.sound_objects
        self.plugin_manager = PluginManager(pet=self.pet, window=self)
        self.plugin_manager.load_plugins()

        config_dir = os.path.expanduser("~/.config/neco-arc-GPT")
        os.makedirs(config_dir, exist_ok=True)
        reminder_path = os.path.join(config_dir, "reminders.json")
        if os.path.exists(reminder_path):
            with open(reminder_path, 'r') as file:
                self.active_reminders = json.load(file)
            
            for reminder in self.active_reminders:
                task = reminder_utils.add_reminder(
                    delay_seconds = reminder["delay"],
                    message = reminder["message"],
                    sound_name = reminder["sound"],
                    repeat = reminder["repeat"],
                    pet=self.pet,
                    parent_window=self,
                    sound_objects=self.sound_objects,
                    active_reminders=self.active_reminders,
                    save_reminders_to_file=self.save_reminders_to_file,
                    loop=loop,
                    callback=self.add_task
                )

            # Save new IDs to file
            self.save_reminders_to_file()
            if len(self.active_reminders) != len(self.active_async_tasks):
                print("[Reminder] Warning: Mismatch between reminders and tasks!")
        randomdialogue_path = os.path.join(config_dir, "random_dialogues.json")
        if os.path.exists(randomdialogue_path):
            with open(randomdialogue_path, "r") as file:
                self.random_dialogues = json.load(file)
        else:
            with open(randomdialogue_path, "w") as file:
                json.dump({"dialogue": "test dialogue :3"}, file, indent=2)

        self.image = Gtk.Image()
        self.add(self.image)

        self.connect("destroy", Gtk.main_quit)
        self.connect("button-press-event", self.on_button_press)
        self.connect("button-release-event", self.on_button_release)
        self.connect("motion-notify-event", self.on_motion_notify)

        self.show_all()

        first_state = next(iter(self.states.values()))
        self.set_default_size((first_state.w), first_state.h)
        self.move(45, 800)

        def periodic_random_function():
            self.random_dialogue()
            next_delay = random.randint(120000, 300000)
            GLib.timeout_add(next_delay, periodic_random_function)
            return False

        # Start the first timeout (initial delay)
        GLib.timeout_add(random.randint(120000, 300000), periodic_random_function)
        GLib.timeout_add(100, self.update_frame)
        GLib.timeout_add(30, self.update_dialogue_bubble)

    def create_event_func(self, event, pet):
        if event["type"] == "state_change":
            return lambda _: pet.set_state(event["new_state"])
        elif event["type"] == "chatgpt":
            return lambda _: pet.start_chat(event["prompt"], event["listen_state"], event["response_state"], event["end_state"])

    def _on_click_event(self, event, func):
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            func(event)

    def update_frame(self):
        pixbuf = self.pet.next_frame()
        self.image.set_from_pixbuf(pixbuf)
        self.move(self.pet.x, self.pet.y)
        return True

    def update_dialogue_bubble(self):
        if hasattr(self, "dialogue_bubble") and self.dialogue_bubble:
            pet_x, pet_y = self.get_position()
            pet_w, _ = self.get_size()
            self.dialogue_bubble.move_to_pet(pet_x, pet_y, pet_w)
        return True

    def on_button_press(self, widget, event):
        if event.button == 1:
            self.dragging = True
            self.drag_offset_x = event.x
            self.drag_offset_y = event.y
            self._mouse_was_drag = False
            return True

        if event.button == 3:
            self.create_context_menu(event)
            return True
        return False

    def create_context_menu(self, event):
        create_context_menu(
            window=self,
            event=event,
            plugin_entries=self.plugin_manager.get_menu_entries(),
            show_reminders_callback=lambda _: reminder_utils.show_reminders_dialog(
                active_async_tasks=self.active_async_tasks,
                parent_window=self,
                active_reminders=self.active_reminders,
                delete_callback=self.delete_reminder,
                save_reminders_to_file=self.save_reminders_to_file,
            ),
            set_reminder_callback=lambda _: reminder_utils.set_reminder_dialog(
                parent_window=self,
                active_reminders=self.active_reminders,
                save_reminders_to_file=self.save_reminders_to_file,
                pet=self.pet,
                sound_objects=self.sound_objects,
                loop=self.loop,
                callback=self.add_task
            ),
            play_sound_callback=lambda _: self.play_random_sound(),
            quit_callback=self.on_quit_activated
        )

    def on_motion_notify(self, widget, event):
        if self.dragging:
            self._mouse_was_drag = True
            new_x = int(event.x_root - self.drag_offset_x)
            new_y = int(event.y_root - self.drag_offset_y)
            self.move(new_x, new_y)
            self.pet.x = new_x
            self.pet.y = new_y
        return True

    def on_button_release(self, widget, event):
        if event.button == 1:
            self.dragging = False
            if not self._mouse_was_drag:
                self.random_dialogue()
        return True

    def play_random_sound(self):
        sounds = list(self.sound_objects.values())
        if sounds:
            random.choice(sounds).play()

    def show_reminders(self):
        reminder_utils.show_reminders_dialog(
            parent_window=self,
            active_reminders=self.active_reminders,
            active_async_tasks=self.active_async_tasks,
            delete_callback=self.delete_reminder,
            save_reminders_to_file=self.save_reminders_to_file
        )

    def open_reminder_dialog(self):
        reminder_utils.reminder_dialog(
            parent_window=self,
            active_reminders=self.active_reminders,
            save_reminders_to_file=self.save_reminders_to_file,
            pet=self.pet,
            sound_objects=self.sound_objects
        )

    def open_alarm_dialog(self):
        if not hasattr(self, "active_alarms"):
            self.active_alarms = []
        alarm_utils.alarm_dialog(
            parent_window=self,
            active_alarms=self.active_alarms,
            save_alarms_to_file=self.save_alarms_to_file,
            pet=self.pet,
            sound_objects=self.sound_objects
        )

    def save_alarms_to_file(self):
        config_dir = os.path.expanduser("~/.config/neco-arc-GPT")
        os.makedirs(config_dir, exist_ok=True)
        path = os.path.join(config_dir, "alarms.json")
        with open(path, "w") as f:
            json.dump(self.active_alarms, f, indent=2)

    def add_task(self, task):
        self.active_async_tasks.append(task)

    def delete_reminder(self, index):
        print(self.active_async_tasks)
        print(self.active_reminders)
        if 0 <= index < len(self.active_reminders):
            print(f"[Reminder] Deleting reminder at index {index}")
            try:
                task = self.active_async_tasks[index]
                task.cancel()
                print(f"[Reminder] Cancelled task at index {index}")
            except IndexError:
                print("[Reminder] No task found to cancel at that index.")

            removed = self.active_reminders.pop(index)
            self.active_async_tasks.pop(index) 

            print(f"[Reminder] Removed reminder: {removed}")
            self.save_reminders_to_file()


    def save_reminders_to_file(self):
        config_dir = os.path.expanduser("~/.config/neco-arc-GPT")
        os.makedirs(config_dir, exist_ok=True)
        path = os.path.join(config_dir, "reminders.json")

        with open(path, "w") as f:
            json.dump(self.active_reminders, f, indent=2)
    
    def load_reminders_from_file(self):
        config_dir = os.path.expanduser("~/.config/neco-arc-GPT/reminders.json")
        if os.path.exists(config_dir):
            with open(config_dir, "r") as f:
                try:
                    self.active_reminders = json.load(f)
                except json.JSONDecodeError:
                    self.active_reminders = []
        else:
            self.active_reminders = []

    def on_delete_event(self, widget, event):
        if self.confirm_quit():
            Gtk.main_quit()
            return False
        else:
            return True

    def on_quit_activated(self, widget):
        if self.confirm_quit():
            Gtk.main_quit()

    def confirm_quit(self):
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Are you sure you want to quit?"
        )
        response = dialog.run()
        dialog.destroy()
        return response == Gtk.ResponseType.YES

    def show_dialogue_bubble(self, message, duration=5):
        if hasattr(self, "dialogue_bubble") and self.dialogue_bubble:
            self.dialogue_bubble.close_bubble()
        anim = ["begin_talking", "shrug"]
        self.pet.set_state(random.choice(anim))

        bubble = DialogueBubble(message, duration=duration, parent=self)
        bubble.on_close_callback = lambda: self.pet.set_state("idle")
        pet_x, pet_y = self.get_position()
        pet_w, _ = self.get_size()
        bubble.move_to_pet(pet_x, pet_y, pet_w)
        self.dialogue_bubble = bubble

    def random_dialogue(self):
        self.show_dialogue_bubble(random.choice(self.random_dialogues)["dialogue"], duration=10)
        self.play_random_sound()