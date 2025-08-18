import os, asyncio
from gi.repository import Gtk, GLib
from functools import partial

def set_reminder_dialog(parent_window, active_reminders, save_reminders_to_file, pet, sound_objects, scripts, loop, callback, run_script):
    dialog = Gtk.Dialog(
        title="Set Reminder",
        transient_for=parent_window,
        flags=0
    )
    dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)

    box = dialog.get_content_area()
    box.set_spacing(8)

    box.add(Gtk.Label(label="Enter reminder message:"))
    entry_message = Gtk.Entry()
    box.add(entry_message)

    box.add(Gtk.Label(label="Enter delay (e.g. 10s, 5m, 2h, 1d):"))
    entry_delay = Gtk.Entry()
    entry_delay.set_placeholder_text("10s, 5m, 2h, 1d")
    box.add(entry_delay)

    repeat_check = Gtk.CheckButton(label="Repeat reminder")
    box.add(repeat_check)

    box.add(Gtk.Label(label="Choose sound:"))
    sound_store = Gtk.ListStore(str)
    for sound in sound_objects.keys():
        sound_store.append([sound])
    sound_combo = Gtk.ComboBox.new_with_model(sound_store)
    renderer_text = Gtk.CellRendererText()
    sound_combo.pack_start(renderer_text, True)
    sound_combo.add_attribute(renderer_text, "text", 0)
    sound_combo.set_active(0)
    box.add(sound_combo)

    box.add(Gtk.Label(label="Attach script:"))
    script_store = Gtk.ListStore(str)
    script_store.append(["None"])
    for script in scripts:
        script_store.append([script])
    script_combo = Gtk.ComboBox.new_with_model(script_store)
    renderer_text = Gtk.CellRendererText()
    script_combo.pack_start(renderer_text, True)
    script_combo.add_attribute(renderer_text, "text", 0)
    script_combo.set_active(0)
    box.add(script_combo)

    #for later...
    # # sound_button = Gtk.Button(label="Add Sound...")
    # # box.add(sound_button)
    # # sound_label = Gtk.Label(label="No file selected")
    # # box.add(sound_label)

    # selected_sound = [None]  # mutable container to hold selected sound file path

    dialog.show_all()
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        message = entry_message.get_text().strip()
        delay_str = entry_delay.get_text().strip()
        repeat = repeat_check.get_active()

        sound_iter = sound_combo.get_active_iter()
        sound_name = None
        if sound_iter:
            sound_name = sound_store[sound_iter][0]

        script_iter = script_combo.get_active_iter()
        script_name = None
        if script_iter and script_iter != "None":
            script_name = script_store[script_iter][0]

        delay_seconds = parse_delay(delay_str)
        if delay_seconds is None:
            print("Invalid delay format.")
            dialog.destroy()
            return None, None 

        # Add reminder data only (no task)
        active_reminders.append({
            "message": message,
            "delay": delay_seconds,
            "repeat": repeat,
            "sound": sound_name,
            "script": script_name
        })
        save_reminders_to_file()

        # Create and return the asyncio task
        reminder_task = add_reminder(
            delay_seconds,
            parent_window,
            message,
            pet,
            sound_objects,
            scripts,
            sound_name,
            script_name,
            repeat,
            active_reminders,
            save_reminders_to_file,
            loop,
            callback,
            run_script
        )
        dialog.destroy()
        return reminder_task, active_reminders[-1]  # Return task and reminder dict

    dialog.destroy()
    return None, None


def add_reminder(delay_seconds, parent_window, message, pet, sound_objects, scripts, sound_name, script_name, repeat, active_reminders, save_reminders_to_file, loop, callback, run_script):
    async def reminder_task():
        print(f"[Reminder] Scheduled: {message} in {delay_seconds}s (repeat={repeat})")
        
        while True:
            await asyncio.sleep(delay_seconds)
            print(f"[Reminder] Triggering: {message}")

            # Show reminder and play sound on main GTK thread
            def trigger_and_cleanup():
                show_reminder(parent_window, message, pet, sound_objects, scripts, sound_name, script_name, run_script)
                if not repeat:
                    # Cleanup only once
                    remove_reminder_by_identity(message, delay_seconds, repeat, sound_name, script_name,active_reminders, save_reminders_to_file)
                return False  # Run once

            GLib.idle_add(trigger_and_cleanup)

            if not repeat:
                break

    # Run the coroutine in the provided loop
    task = asyncio.run_coroutine_threadsafe(reminder_task(), loop)
    callback(task)
    return task

def remove_reminder_by_identity(message, delay, repeat, sound_name, script_name, active_reminders, save_reminders_to_file):
    for i, rem in enumerate(active_reminders):
        if rem["message"] == message and rem["delay"] == delay and rem.get("repeat", False) == repeat and rem["sound"] == sound_name and rem["script"] == script_name:
            print(f"[Reminder] Removing one-time reminder: {rem}")
            del active_reminders[i]
            save_reminders_to_file()
            break

def show_reminder(parent_window, message, pet, sound_objects, scripts, sound_name=None, script_name=None, run_script=None):
    dialog = Gtk.MessageDialog(
        parent=parent_window,
        modal=True,
        destroy_with_parent=True,
        message_type=Gtk.MessageType.INFO,
        buttons=Gtk.ButtonsType.OK,
        text="Reminder"
    )
    dialog.format_secondary_text(message)
    pet.set_state("excite")

    #play sound
    if sound_name and sound_name in sound_objects:
        sound_objects[sound_name].play()
    elif "ima_doko" in sound_objects:
        sound_objects["ima_doko"].play()
    
    #if script run
    if script_name in scripts:
        try:
            print(f"[Reminder] Running '{script_name}'")
            run_script(script_name, parent_window)
        except Exception as e:
            print(f"[Reminder] Error while trying to run '{script_name}': {e}")

    dialog.run()
    dialog.destroy()
    pet.set_state("idle")
    return True


def delete_reminder(index, active_reminders, active_async_tasks, save_reminders_to_file):
    if 0 <= index < len(active_reminders):
        removed = active_reminders.pop(index)
        # Cancel corresponding asyncio task if exists
        if 0 <= index < len(active_async_tasks):
            task = active_async_tasks.pop(index)
            if task:
                task.cancel()
        save_reminders_to_file()
        print(f"Deleted reminder: {removed['message']}")


def show_reminders_dialog(parent_window, active_reminders, active_async_tasks, delete_callback, save_reminders_to_file):
    dialog = Gtk.Dialog(
        title="Active Reminders",
        transient_for=parent_window,
        flags=0
    )
    dialog.add_buttons(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)

    box = dialog.get_content_area()
    box.set_spacing(6)

    if not active_reminders:
        box.add(Gtk.Label(label="No active reminders."))
    else:
        for i, reminder in enumerate(active_reminders):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            message = reminder['message']
            delay = reminder['delay']
            repeat = reminder.get('repeat', False)
            label_text = f"{message} - {'every' if repeat else 'in'} {delay}s"
            label = Gtk.Label(label=label_text)
            label.set_xalign(0)
            row.pack_start(label, True, True, 0)

            del_button = Gtk.Button(label="Delete")
            del_button.connect(
                "clicked",
                lambda btn, idx=i: _delete_and_refresh(
                    dialog,
                    idx,
                    active_reminders,
                    active_async_tasks,
                    delete_callback,
                    save_reminders_to_file,
                    parent_window
                )
            )
            row.pack_start(del_button, False, False, 0)
            box.add(row)

    dialog.show_all()
    dialog.run()
    dialog.destroy()


def _delete_and_refresh(dialog, index, active_reminders, active_async_tasks, delete_callback, save_reminders_to_file, parent_window):
    dialog.destroy()
    delete_callback(index)
    show_reminders_dialog(parent_window, active_reminders, active_async_tasks, delete_callback, save_reminders_to_file)


def parse_delay(delay_str):
    try:
        unit = delay_str[-1].lower()
        number = int(delay_str[:-1])
        if unit == 's':
            return number
        elif unit == 'm':
            return number * 60
        elif unit == 'h':
            return number * 3600
        elif unit == 'd':
            return number * 86400
        else:
            return int(delay_str)
    except Exception:
        return None
