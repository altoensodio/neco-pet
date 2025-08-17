import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

def reload_plugins(plugin_entries, load_plugins, window):
    for plugin in plugin_entries:
        if plugin["plugin"].get("stop"):
            plugin["plugin"]["stop"](window.pet)
    load_plugins()

def create_context_menu(
    window,
    event,
    load_plugins,
    loaded_scripts,
    run_script,
    load_scripts,
    plugin_entries,
    show_reminders_callback,
    set_reminder_callback,
    quit_callback
):
    menu = Gtk.Menu()

    # Submenus
    timers_menu = Gtk.Menu()
    reminder_menu = Gtk.Menu()
    alarm_menu = Gtk.Menu()
    plugins_menu = Gtk.Menu()
    scripts_menu = Gtk.Menu()

    #Plugins Submenu
    # Reload Plugins
    plugin_reload = Gtk.MenuItem(label="Reload Plugins")
    plugin_reload.connect("activate", lambda w: reload_plugins(plugin_entries, load_plugins, window))
    plugins_menu.append(plugin_reload)

    plugins_menu.append(Gtk.SeparatorMenuItem())

    # Load plugin items
    if plugin_entries:
        for entry in sorted(plugin_entries, key=lambda e: e["plugin"]["label"]):
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

    #Scripts Submenu
    # Reload Scripts
    script_reload = Gtk.MenuItem(label="Reload Scripts")
    script_reload.connect("activate", lambda _: load_scripts())
    scripts_menu.append(script_reload)

    scripts_menu.append(Gtk.SeparatorMenuItem())

    if loaded_scripts:
        for script_name in loaded_scripts:
            item = Gtk.MenuItem(label=script_name)
            item.connect("activate", lambda w, name=script_name: run_script(name, window))
            scripts_menu.append(item)
    else:
        no_scripts_item = Gtk.MenuItem(label="No scripts available")
        no_scripts_item.set_sensitive(False)
        scripts_menu.append(no_scripts_item)

    scripts_menu.show_all()
    scripts_menu_item = Gtk.MenuItem(label="Scripts")
    scripts_menu_item.set_submenu(scripts_menu)
    menu.append(scripts_menu_item)

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
    menu.append(Gtk.SeparatorMenuItem())
    # Quit item
    quit_item = Gtk.MenuItem(label="Quit")
    quit_item.connect("activate", quit_callback)
    menu.append(quit_item)
    # Optional Close (no-op)
    close_item = Gtk.MenuItem(label="Close")
    menu.append(close_item)

    menu.show_all()
    menu.popup_at_pointer(event)
