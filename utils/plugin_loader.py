import os
import importlib.util

def load_plugin_file(path):
    """Import a Python file and return its module if valid."""
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"[PluginLoader] Error loading {name}: {e}")
        return None

def discover_plugins(plugin_dir="plugins"):
    """Discover and return modules from valid plugin files."""
    plugins = []
    if not os.path.isdir(plugin_dir):
        print(f"[PluginLoader] Plugin directory {plugin_dir} not found.")
        return plugins

    for fname in os.listdir(plugin_dir):
        if fname.endswith(".py") and not fname.startswith("__"):
            path = os.path.join(plugin_dir, fname)
            module = load_plugin_file(path)
            if module:
                plugins.append(module)
    return plugins