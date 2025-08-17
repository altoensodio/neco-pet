import os, sys, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from core.window import NecoArcWindow
from core.async_runner import get_event_loop

if __name__ == "__main__":
    assets_path = sys.argv[1] if len(sys.argv) >= 2 else os.path.join("assets", "neco_arc")
    win = NecoArcWindow(assets_path, loop=get_event_loop())
    Gtk.main()
