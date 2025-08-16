from utils import plugin_loader

class PluginManager:
    def __init__(self, pet=None, window=None, plugin_dir="plugins"):
        self.pet = pet
        self.window = window
        self.plugin_dir = plugin_dir
        self.plugins = []           # Loaded plugin modules
        self.menu_entries = []      # List of dicts: {label, callback, menu_item_ref}

    def load_plugins(self):
        self.plugins = plugin_loader.discover_plugins(self.plugin_dir)
        self.menu_entries.clear()

        for mod in self.plugins:
            if hasattr(mod, "init") and callable(mod.init):
                try:
                    mod.init()
                except Exception as e:
                    print(f"[PluginManager] Error in init() for {mod.__name__}: {e}")

            plugin = getattr(mod, "plugin", None)
            if isinstance(plugin, dict):
                label = plugin.get("label")
                callback = plugin.get("callback")
                menu_item_ref = plugin.get("menu_item_ref", None)  # grab ref dict if exists
                if label and callable(callback):
                    self.menu_entries.append({
                        "plugin": plugin,  # store the live plugin object
                        "callback": lambda *a, f=callback: f(self.pet, self.window),
                        "menu_item_ref": plugin.get("menu_item_ref"),
                    })
                else:
                    print(f"[PluginManager] Skipped invalid plugin: {mod}")
            else:
                print(f"[PluginManager] No 'plugin' dict in {mod.__name__}")

    def get_menu_entries(self):
        return self.menu_entries
