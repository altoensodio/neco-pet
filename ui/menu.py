import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

def create_context_menu(
    window,
    event,
    plugin_entries,
    show_reminders_callback,
    set_reminder_callback,
    play_sound_callback,
    quit_callback
):
    menu = Gtk.Menu()

    # Submenus
    timers_menu = Gtk.Menu()
    reminder_menu = Gtk.Menu()
    alarm_menu = Gtk.Menu()
    plugins_menu = Gtk.Menu()
    
    #Plugins Submenu
    # Load plugin items
    if plugin_entries:
        for entry in plugin_entries:
            label = entry["plugin"]["label"]
            menu_item = Gtk.MenuItem(label=label)
            menu_item_ref = entry.get("menu_item_ref")
            if menu_item_ref is not None:
                menu_item_ref["item"] = menu_item  # assign Gtk widget to plugin's ref dict

            menu_item.connect("activate", entry["callback"])
            plugins_menu.append(menu_item)
    else:
        no_plugins_item = Gtk.MenuItem(label="No plugins available")
        no_plugins_item.set_sensitive(False)
        plugins_menu.append(no_plugins_item)

    plugins_menu.show_all()
    plugins_menu_item = Gtk.MenuItem(label="Plugins")
    plugins_menu_item.set_submenu(plugins_menu)
    menu.append(plugins_menu_item)

    # Reminder Submenu
    show_item = Gtk.MenuItem(label="Show Reminders")
    show_item.connect("activate", show_reminders_callback)
    reminder_menu.append(show_item)

    reminder_item = Gtk.MenuItem(label="Set Reminder")
    reminder_item.connect("activate", set_reminder_callback)
    reminder_menu.append(reminder_item)

    reminder_menu_item = Gtk.MenuItem(label="Reminders")
    reminder_menu_item.set_submenu(reminder_menu)
    timers_menu.append(reminder_menu_item)

    alarm_item = Gtk.MenuItem(label="Alarms (Coming Soon)")
    timers_menu.append(alarm_item)  # Placeholder for future

    timers_menu.show_all()
    timers_menu_item = Gtk.MenuItem(label="Timers")
    timers_menu_item.set_submenu(timers_menu)
    menu.append(timers_menu_item)

    # Play random sound
    sound_item = Gtk.MenuItem(label="Play Random Sound")
    sound_item.connect("activate", play_sound_callback)
    menu.append(sound_item)

    # Quit item
    quit_item = Gtk.MenuItem(label="Quit")
    quit_item.connect("activate", quit_callback)
    menu.append(quit_item)

    # Optional Close (no-op)
    close_item = Gtk.MenuItem(label="Close")
    menu.append(close_item)

    menu.show_all()
    menu.popup_at_pointer(event)
