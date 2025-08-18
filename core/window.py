import json, pygame
from os import makedirs
from os.path import join, expanduser, exists
from pygame import mixer
from gi import require_versions
require_versions({'Gtk': '3.0', 'GdkPixbuf': '2.0'})
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
from typing import Callable
from random import randint, choice
from pet import Pet, PetState
from utils import reminder_utils, alarm_utils
from ui import create_context_menu
from core import PluginManager, SoundManager, ScriptManager, ReminderManager, DialogueManager

class NecoArcWindow(Gtk.Window):   
    def __init__(self, assets_path, loop):
        #gtk stuff
        super().__init__(title="Cage")
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.image = Gtk.Image()
        self.add(self.image)

        #async loop
        self.loop = loop

        #drag values
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        self.config_dir = expanduser("~/.config/neco-pet")

        #Pet state and stuff
        config_obj = self.json_handler(join(assets_path, "config.json"))
        self.states = {state['state_name']: PetState(state, assets_path) for state in config_obj["states"]}
        for state in self.states.values():
            for next_state in state.next_states.names:
                assert next_state in self.states
        self.pet = Pet(self.states, self)

        #start sound and related
        try:
            self.sound_manager = SoundManager()
        except pygame.error as e:
            print(f"[Sound Error] Could not initialize audio: {e}")

        #create .config dir
        makedirs(self.config_dir, exist_ok=True)

        #load dialogues
        self.dialogue_manager = DialogueManager(window=self, pet=self.pet, config_dir=self.config_dir)
        self.dialogue_manager.load_random_dialogues()

        #load plugin and scripts
        self.load_plugins()
        self.load_scripts()

        #reminder system stuff
        self.reminder_manager = ReminderManager(
            window=self,
            config_dir=self.config_dir,
            loop=self.loop,
            pet=self.pet,
            sound_objects=self.sound_manager.get_sound_objects(),
            script_manager=self.script_manager,
            json_handler=self.json_handler
        )

        self.reminder_manager.load_from_file()
        self.reminder_manager.reactivate_reminders()

        #button presses handlers and others
        self.connect("destroy", Gtk.main_quit)
        self.connect("delete-event", self.on_delete_event)
        self.connect("button-press-event", self.on_button_press)
        self.connect("button-release-event", self.on_button_release)
        self.connect("motion-notify-event", self.on_motion_notify)

        self.show_all()

        first_state = next(iter(self.states.values()))
        self.set_default_size((first_state.w), first_state.h)
        self.move(45, 800)

        #random dialogue timer
        def periodic_random_dialogue():
            self.dialogue_manager.random_dialogue()
            next_delay = randint(120000, 300000)
            GLib.timeout_add(next_delay, periodic_random_dialogue)
            return False

        #timeouts
        GLib.timeout_add(randint(120000, 300000), periodic_random_dialogue) # between 2 and 5min
        GLib.timeout_add(100, self.update_frame)
        GLib.timeout_add(30, self.dialogue_manager.update_dialogue_bubble)

    def json_handler(self, path, write=False, data=None, default=None):
        try:
            if write:
                with open(path, "w") as f:
                    json.dump(data, f, indent=2)
            else:
                with open(path) as f:
                    return json.load(f)
        except Exception as e:
            print(f"[JSON Handler] Error accessing {path}: {e}")
            return default if default is not None else []

    #Plugin and script load
    def load_plugins(self):
        self.plugin_manager = PluginManager(pet=self.pet, window=self)
        self.plugin_manager.load_plugins()
    
    def load_scripts(self):
        self.script_manager = ScriptManager()
        self.script_manager.load_scripts()
    #--

    #Core window updates
    def update_frame(self):
        pixbuf = self.pet.next_frame()
        self.image.set_from_pixbuf(pixbuf)
        self.move(self.pet.x, self.pet.y)
        return True
    #--

    #Button press stuff
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

    def _on_click_event(self, event, func):
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            func(event)

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
                self.dialogue_manager.random_dialogue()
        return True
    #--

    #i hate this block of code (it does what it says)
    def create_context_menu(self, event):
        create_context_menu(
            window=self,
            event=event,
            run_script=lambda name, window: self.script_manager.run_script(name, window),
            load_scripts=lambda: self.load_scripts(),
            load_plugins=lambda: self.load_plugins(),
            loaded_scripts=self.script_manager.get_scripts(),
            plugin_entries=self.plugin_manager.get_menu_entries(),
            show_reminders_callback=lambda _: reminder_utils.show_reminders_dialog(
                active_async_tasks=self.reminder_manager.active_async_tasks,
                parent_window=self,
                active_reminders=self.reminder_manager.active_reminders,
                delete_callback=self.reminder_manager.delete_reminder,
                save_reminders_to_file=self.reminder_manager.save_to_file,
            ),
            set_reminder_callback=lambda _: reminder_utils.set_reminder_dialog(
                parent_window=self,
                active_reminders=self.reminder_manager.active_reminders,
                save_reminders_to_file=self.reminder_manager.save_to_file,
                pet=self.pet,
                scripts=self.script_manager.get_scripts(),
                sound_objects=self.sound_manager.get_sound_objects(),
                loop=self.loop,
                callback=self.reminder_manager.add_task,
                run_script=self.script_manager.run_script
            ),
            quit_callback=self.on_quit_activated
        )
    #--

    #Quit stuff
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
    #--