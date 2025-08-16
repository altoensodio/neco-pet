import gi, cairo, math
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

class DialogueBubble(Gtk.Window):
    WIDTH = 300
    HEIGHT = 100
    TAIL_HEIGHT = 20

    def __init__(self, message, duration=5, parent=None):
        super().__init__(type=Gtk.WindowType.POPUP)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_app_paintable(True)
        self.set_resizable(False)
        self.duration = duration
        self.parent = parent
        self.message = message
        self.on_close_callback = None

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(self.WIDTH, self.HEIGHT + self.TAIL_HEIGHT)
        self.drawing_area.connect("draw", self.on_draw)
        self.add(self.drawing_area)

        self.show_all()

        self.timeout_id = GLib.timeout_add_seconds(duration, self.close_bubble)
        self.connect("button-press-event", lambda *_: self.close_bubble())

    def on_draw(self, widget, cr):
        WIDTH = self.WIDTH
        TAIL_HEIGHT = self.TAIL_HEIGHT
        RADIUS = 12

        # Set font before measuring/wrapping text
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(14)

        max_text_width = 260  # padding 20 on each side in a 300 width bubble
        wrapped_lines = self.wrap_text_to_width(cr, self.message, max_text_width)

        line_height = 20
        padding = 40  # top + bottom padding for the bubble content
        bubble_height = padding + len(wrapped_lines) * line_height

        # Update internal height and drawing area size dynamically
        self.HEIGHT = bubble_height
        self.drawing_area.set_size_request(WIDTH, bubble_height + TAIL_HEIGHT)

        HEIGHT = self.HEIGHT

        cr.set_source_rgba(0, 0, 0, 0)  # Transparent background
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        # White fill for bubble
        cr.set_source_rgba(1, 1, 1, 0.95)

        x = 10
        y = 10
        w = WIDTH - 20
        h = HEIGHT - 20

        # Rounded rectangle + tail path (connected border)
        cr.new_path()
        cr.arc(x + w - RADIUS, y + RADIUS, RADIUS, -math.pi / 2, 0)
        cr.arc(x + w - RADIUS, y + h - RADIUS, RADIUS, 0, math.pi / 2)
        cr.line_to(x + w // 2 + 10, y + h)
        cr.line_to(x + w // 2, y + h + TAIL_HEIGHT)
        cr.line_to(x + w // 2 - 10, y + h)
        cr.arc(x + RADIUS, y + h - RADIUS, RADIUS, math.pi / 2, math.pi)
        cr.arc(x + RADIUS, y + RADIUS, RADIUS, math.pi, 3 * math.pi / 2)
        cr.close_path()

        cr.fill_preserve()

        # Black border stroke
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(2)
        cr.stroke()

        # Draw wrapped text inside bubble
        cr.set_source_rgb(0, 0, 0)
        x_text = 20
        y_text = 35
        for line in wrapped_lines:
            cr.move_to(x_text, y_text)
            cr.show_text(line)
            y_text += line_height

        return False


    def rounded_rectangle(self, cr, x, y, w, h, r):
        cr.new_sub_path()
        cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
        cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
        cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
        cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
        cr.close_path()

    def move_to_pet(self, pet_x, pet_y, pet_w):
        offset_x = pet_x + pet_w // 2 - self.WIDTH // 2
        offset_y = pet_y - self.HEIGHT + 10
        self.move(offset_x, offset_y)

    def close_bubble(self):
        if self.on_close_callback:
            self.on_close_callback()
        if self.timeout_id:
            GLib.source_remove(self.timeout_id)
            self.timeout_id = None
        self.destroy()
        if self.parent:
            self.parent.dialogue_bubble = None
        return False

    def wrap_text_to_width(self, cr, text, max_width):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            extents = cr.text_extents(test_line)
            if extents.width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines
