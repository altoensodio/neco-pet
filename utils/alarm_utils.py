from gi.repository import Gtk, GLib
from datetime import datetime, timedelta

def alarm_dialog(parent_window, active_alarms, save_alarms_to_file, pet, sound_objects):
    dialog = Gtk.Dialog(
        title="Set Alarm",
        transient_for=parent_window,
        flags=0
    )
    dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)

    box = dialog.get_content_area()
    box.set_spacing(8)

    box.add(Gtk.Label(label="Enter alarm message:"))
    entry_message = Gtk.Entry()
    box.add(entry_message)

    box.add(Gtk.Label(label="Enter alarm time (24-hour format HH:MM):"))
    entry_time = Gtk.Entry()
    entry_time.set_placeholder_text("14:30")
    box.add(entry_time)

    repeat_check = Gtk.CheckButton(label="Repeat daily")
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

    dialog.show_all()
    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        message = entry_message.get_text().strip()
        time_str = entry_time.get_text().strip()
        repeat = repeat_check.get_active()
        sound_iter = sound_combo.get_active_iter()
        sound_name = None
        if sound_iter:
            sound_name = sound_store[sound_iter][0]

        seconds_until = seconds_until_alarm(time_str)
        if seconds_until is None:
            print("Invalid time format.")
            dialog.destroy()
            return

        def callback():
            show_alarm(parent_window, message, pet, sound_objects, sound_name)
            if not repeat:
                # Remove non-repeat alarm after firing
                to_remove = None
                for alarm in active_alarms:
                    if alarm['message'] == message and alarm['time'] == time_str and alarm.get('repeat', False) == repeat:
                        to_remove = alarm
                        break
                if to_remove:
                    if 'id' in to_remove:
                        try:
                            GLib.source_remove(to_remove['id'])
                        except Exception:
                            pass
                    active_alarms.remove(to_remove)
                    save_alarms_to_file()
            return True if repeat else False

        alarm_id = GLib.timeout_add_seconds(seconds_until, callback)

        active_alarms.append({
            "id": alarm_id,
            "message": message,
            "time": time_str,
            "repeat": repeat,
            "sound": sound_name
        })
        save_alarms_to_file()

    dialog.destroy()


def seconds_until_alarm(time_str):
    try:
        now = datetime.now()
        alarm_time = datetime.strptime(time_str, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        if alarm_time <= now:
            alarm_time += timedelta(days=1)
        return int((alarm_time - now).total_seconds())
    except Exception:
        return None


def show_alarm(parent_window, message, pet, sound_objects, sound_name=None):
    dialog = Gtk.MessageDialog(
        parent=parent_window,
        modal=True,
        destroy_with_parent=True,
        message_type=Gtk.MessageType.INFO,
        buttons=Gtk.ButtonsType.OK,
        text="Alarm"
    )
    dialog.format_secondary_text(message)
    pet.set_state("excite")

    if sound_name and sound_name in sound_objects:
        sound_objects[sound_name].play()
    elif "ima_doko" in sound_objects:
        sound_objects["ima_doko"].play()

    dialog.run()
    dialog.destroy()
    pet.set_state("idle")
    return True
