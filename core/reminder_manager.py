from os.path import join
from os import makedirs
from utils import reminder_utils

class ReminderManager:
    def __init__(self, window, config_dir, loop, pet, sound_objects, script_manager, json_handler):
        self.window = window
        self.config_dir = config_dir
        self.loop = loop
        self.pet = pet
        self.sound_objects = sound_objects
        self.script_manager = script_manager
        self.json_handler = json_handler

        self._active_reminders = []
        self._active_async_tasks = []

    @property
    def active_reminders(self):
        return self._active_reminders

    @active_reminders.setter
    def active_reminders(self, value):
        self._active_reminders = value

    @property
    def active_async_tasks(self):
        return self._active_async_tasks

    @active_async_tasks.setter
    def active_async_tasks(self, value):
        self._active_async_tasks = value

    def load_from_file(self):
        path = join(self.config_dir, "reminders.json")
        self.active_reminders = self.json_handler(path, default=[])

    def save_to_file(self):
        makedirs(self.config_dir, exist_ok=True)
        path = join(self.config_dir, "reminders.json")
        self.json_handler(path, write=True, data=self.active_reminders)

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
            self.save_to_file()

    def reactivate_reminders(self):
        self.load_from_file()
        for reminder in self.active_reminders:
            task = reminder_utils.add_reminder(
                delay_seconds = reminder["delay"],
                message = reminder["message"],
                sound_name = reminder["sound"],
                repeat = reminder["repeat"],
                script_name= reminder["script"],
                pet=self.pet,
                parent_window=self.window,
                sound_objects=self.sound_objects,
                scripts=self.script_manager.get_scripts(),
                active_reminders=self.active_reminders,
                save_reminders_to_file=self.save_to_file,
                loop=self.loop,
                callback=self.add_task,
                run_script=self.script_manager.run_script
            )

        self.save_to_file()

    def show_reminders_dialog(self):
        reminder_utils.show_reminders_dialog(
            parent_window=self.window,
            active_reminders=self.active_reminders,
            active_async_tasks=self.active_async_tasks,
            delete_callback=self.delete_reminder,
            save_reminders_to_file=self.save_to_file
        )

    def open_reminder_dialog(self):
        reminder_utils.reminder_dialog(
            parent_window=self.window,
            active_reminders=self.active_reminders,
            save_reminders_to_file=self.save_to_file,
            pet=self.pet,
            sound_objects=self.sound_objects
        )
