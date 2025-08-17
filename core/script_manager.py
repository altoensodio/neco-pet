import subprocess
from gi.repository import GLib
import os

class ScriptManager:
    def __init__(self, scripts_dir="scripts"):
        self.scripts_dir = scripts_dir
        self.supported_exts = {".sh", ".py"}
        self.scripts = []

    def get_scripts(self):
        return self.scripts

    def load_scripts(self):
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir)
        self.scripts = sorted([
            f for f in os.listdir(self.scripts_dir)
            if os.path.isfile(os.path.join(self.scripts_dir, f))
            and os.path.splitext(f)[1] in self.supported_exts
        ])

    def run_script(self, script_name, window):
        script_path = os.path.join(self.scripts_dir, script_name)

        ext = os.path.splitext(script_path)[1]
        if ext == ".sh":
            cmd = ["bash", script_path]
        elif ext == ".py":
            cmd = ["python3", script_path]
        else:
            GLib.idle_add(window.show_dialogue_bubble, "Unsupported script type.", 10)
            return

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            output = result.stdout.strip() or "Script ran with no output."
            GLib.idle_add(window.show_dialogue_bubble, output, 10)
            window.play_random_sound()
        except Exception as e:
            err = f"Error running script: {e}"
            GLib.idle_add(window.show_dialogue_bubble, err, 10)