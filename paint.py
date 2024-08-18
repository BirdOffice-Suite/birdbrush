import tkinter as tk
import tkinter.colorchooser as colorchooser
import tkinter.filedialog as filedialog
from PIL import Image, ImageTk, ImageDraw
import json

def hex_to_rgb(hex_color):
    """Converts a hex color string to an RGB tuple.

    Args:
        hex_color: The color string in hex format (e.g., "#FF0000") or a valid color name.

    Returns:
        An RGB tuple (e.g., (255, 0, 0)) or None if the color is invalid.
    """
    try:
        hex_color = hex_color.strip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        # Handle non-hex color strings gracefully (e.g., return default color)
        return (0, 0, 0)  # Default black

class PaintApp:
    def __init__(self, master):
        self.master = master
        self.master.title("BirdBrush (BBF version 1)")
        self.master.geometry("700x700")

        self.canvas = tk.Canvas(master, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.color_choice = "black"
        self.line_width = 2
        self.eraser_on = False
        self.fill_on = False

        self.setup_colors()
        self.setup_options()

        self.draw_x, self.draw_y = 0, 0
        self.drawing = False

        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)

    def setup_colors(self):
        self.colors = ["black", "red", "green", "blue", "yellow"]
        color_frame = tk.Frame(self.master)
        color_frame.pack(side=tk.LEFT, fill=tk.Y)

        for color in self.colors:
            button = tk.Button(color_frame, bg=color, width=2, command=lambda c=color: self.set_color(c))
            button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def setup_options(self):
        option_frame = tk.Frame(self.master)
        option_frame.pack(side=tk.RIGHT)

        self.line_width_label = tk.Label(option_frame, text="Line Width:")
        self.line_width_label.pack()

        self.line_width_scale = tk.Scale(option_frame, from_=1, to=50, orient=tk.HORIZONTAL, command=self.set_line_width)
        self.line_width_scale.set(self.line_width)
        self.line_width_scale.pack()

        eraser_button = tk.Button(option_frame, text="Eraser", command=self.toggle_eraser)
        eraser_button.pack()

        color_picker_button = tk.Button(option_frame, text="Color Picker", command=self.pick_color)
        color_picker_button.pack(side=tk.LEFT, expand=True, fill='both')

        save_button = tk.Button(option_frame, text="Save", command=self.save_image)
        save_button.pack(side=tk.LEFT, expand=True, fill='both')

        load_button = tk.Button(option_frame, text="Load", command=self.load_image)
        load_button.pack(side=tk.LEFT, expand=True, fill='both')

    def set_color(self, color):
        self.color_choice = color
        self.eraser_on = False
        self.fill_on = False

    def set_line_width(self, value):
        self.line_width = int(value)

    def toggle_eraser(self):
        self.eraser_on = not self.eraser_on
        self.fill_on = False

    def toggle_fill(self):
        self.fill_on = not self.fill_on
        self.eraser_on = False

    def start_draw(self, event):
        self.draw_x, self.draw_y = event.x, event.y
        self.drawing = True

    def draw(self, event):
        if self.drawing:
            x, y = event.x, event.y
            if self.eraser_on:
                color = "white"
            else:
                color = self.color_choice
            self.bresenham_line(self.draw_x, self.draw_y, x, y, color)
            self.draw_x, self.draw_y = x, y

    def stop_draw(self, event):
        self.drawing = False

    def bresenham_line(self, x1, y1, x2, y2, color):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            self.canvas.create_line(x1, y1, x1 + 1, y1 + 1, fill=color, width=self.line_width)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    def save_image(self):
        file_path = filedialog.asksaveasfilename(filetypes=[("BirdBrush file", "*.bbf"), ("All files", "*.*")], defaultextension=".bbf")
        if file_path:
            lines = []
            for item in self.canvas.find_all():
                item_type = self.canvas.type(item)
                if item_type == "line":
                    coords = self.canvas.coords(item)
                    fill = self.canvas.itemcget(item, "fill")
                    width = self.canvas.itemcget(item, "width")
                    lines.append({"type": "line", "coords": coords, "fill": fill, "width": width})

            with open(file_path, 'w') as f:
                json.dump(lines, f)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("BirdBrush file", "*.bbf"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'r') as f:
                lines = json.load(f)

            self.canvas.delete("all")
            for line in lines:
                if line["type"] == "line":
                    self.canvas.create_line(line["coords"], fill=line["fill"], width=line["width"])

    def pick_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.color_choice = color

root = tk.Tk()
app = PaintApp(root)
root.mainloop()
