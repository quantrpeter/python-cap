#!/usr/bin/env python3
"""
Cross-platform screencap tool. Press Ctrl+Cmd+3 (Mac) or Ctrl+Alt+3 (Windows/Linux) to capture.
After capture, annotate with colors, arrow, rect, circle, and brush.
"""

import os
import signal
import sys
import threading
import platform
from datetime import datetime

import mss
from PIL import Image, ImageGrab, ImageTk
from pynput import keyboard

# Tkinter is in different places on Python 3
if sys.version_info >= (3, 0):
    import tkinter as tk
else:
    import Tkinter as tk

# --- Config ---
_IS_MAC = platform.system() == "Darwin"
HOTKEY = "<ctrl>+<cmd>+3" if _IS_MAC else "<ctrl>+<alt>+3"  # Ctrl+Cmd+3 on Mac, Ctrl+Alt+3 on Win/Ubuntu
COLORS = [
    "#e74c3c",  # red
    "#3498db",  # blue
    "#2ecc71",  # green
    "#000000",  # black
    "#f1c40f",  # yellow
    "#9b59b6",  # purple
]
TOOL_ARROW = "arrow"
TOOL_RECT = "rect"
TOOL_CIRCLE = "circle"
TOOL_BRUSH = "brush"
BRUSH_WIDTH = 4
LINE_WIDTH = 3


def _desktop_path():
    """Return the user's Desktop directory for the current platform."""
    if platform.system() == "Windows":
        return os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
    return os.path.expanduser(
        os.environ.get("XDG_DESKTOP_DIR", "~/Desktop")
    )


# --- Screenshot ---
def capture_screen(region=None):
    """Capture full screen or region. region = (x, y, w, h) or None for full screen. Returns PIL Image (RGB)."""
    with mss.mss() as sct:
        if region is None:
            monitor = sct.monitors[0]
            shot = sct.grab(monitor)
        else:
            x, y, w, h = region
            shot = sct.grab({"left": x, "top": y, "width": w, "height": h})
        img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
        return img


# --- Region selector (drag to select portion of screen) ---
class RegionSelector:
    def __init__(self, parent_root, full_image, on_done):
        self.on_done = on_done
        self.full_image = full_image
        self.start_x = self.start_y = None
        self.rect_id = None

        self.win = tk.Toplevel(parent_root)
        self.win.attributes("-topmost", True)
        self.win.overrideredirect(True)
        self.win.geometry(f"{full_image.width}x{full_image.height}+0+0")
        self.win.configure(bg="black")

        self.canvas = tk.Canvas(
            self.win,
            width=full_image.width,
            height=full_image.height,
            highlightthickness=0,
            bg="black",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.photo = ImageTk.PhotoImage(full_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.win.bind("<Escape>", lambda e: self._cancel())

        # Hint (dark text on light bar so it's always readable)
        self.canvas.create_rectangle(0, 0, full_image.width, 44, fill="#e8e8e8", outline="")
        self.canvas.create_text(
            full_image.width // 2,
            22,
            text="Drag to select region · Esc to cancel",
            fill="#1a1a1a",
            font=("", 14),
        )

    def _on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect_id is not None:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="#00b4ff", width=2, dash=(6, 4),
        )

    def _on_drag(self, event):
        if self.rect_id is not None:
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def _on_release(self, event):
        if self.rect_id is None:
            return
        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y
        left, right = min(x1, x2), max(x1, x2)
        top, bottom = min(y1, y2), max(y1, y2)
        w, h = right - left, bottom - top
        if w >= 10 and h >= 10:
            cropped = self.full_image.crop((left, top, right, bottom))
            self.win.destroy()
            self.on_done(cropped)
        else:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
        self.start_x = self.start_y = None

    def _cancel(self):
        self.win.destroy()
        self.on_done(None)


# --- Annotation window ---
class AnnotationWindow:
    def __init__(self, root, pil_image):
        self.root = root
        self.pil_image = pil_image
        self.current_color = COLORS[0]
        self.current_tool = TOOL_BRUSH
        self.start_x = self.start_y = None
        self.current_item = None
        self.brush_line = []

        # Scale image to fit screen
        max_w = root.winfo_screenwidth() - 80
        max_h = root.winfo_screenheight() - 160
        w, h = pil_image.size
        scale = min(max_w / w, max_h / h, 1.0)
        self.display_w = int(w * scale)
        self.display_h = int(h * scale)
        self.scale = scale
        resample = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
        self.display_image = pil_image.resize((self.display_w, self.display_h), resample)

        root.title("Screencap – Annotate")
        root.configure(bg="#2c3e50")

        # Toolbar frame
        toolbar = tk.Frame(root, bg="#2c3e50", pady=6, padx=6)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Colors (use Frame so the color actually shows on macOS/Windows)
        tk.Label(toolbar, text="Color:", bg="#2c3e50", fg="#1a1a1a", font=("", 10)).pack(side=tk.LEFT, padx=(0, 6))
        for c in COLORS:
            f = tk.Frame(toolbar, width=24, height=24, bg=c, highlightbackground="#555", highlightthickness=1)
            f.pack(side=tk.LEFT, padx=2)
            f.pack_propagate(False)
            f.bind("<Button-1>", lambda e, col=c: self._set_color(col))
            # Make it look clickable
            f.bind("<Enter>", lambda e, fr=f: fr.configure(highlightbackground="#fff", highlightthickness=2))
            f.bind("<Leave>", lambda e, fr=f: fr.configure(highlightbackground="#555", highlightthickness=1))
        tk.Frame(toolbar, width=20).pack(side=tk.LEFT)

        # Tools
        tk.Label(toolbar, text="Tools:", bg="#2c3e50", fg="#1a1a1a", font=("", 10)).pack(side=tk.LEFT, padx=(0, 6))
        self._tool_btns = {}
        for name, label in [
            (TOOL_ARROW, "Arrow"),
            (TOOL_RECT, "Rect"),
            (TOOL_CIRCLE, "Circle"),
            (TOOL_BRUSH, "Brush"),
        ]:
            b = tk.Button(
                toolbar,
                text=label,
                bg="#34495e",
                fg="#1a1a1a",
                activebackground="#1abc9c",
                activeforeground="white",
                relief=tk.FLAT,
                padx=8,
                pady=4,
                font=("", 10),
                command=(lambda t=name: self._set_tool(t)),
            )
            b.pack(side=tk.LEFT, padx=2)
            self._tool_btns[name] = b
        self._update_tool_buttons()

        # Canvas with image (ImageTk is cross-platform)
        self.photo = ImageTk.PhotoImage(self.display_image)

        self.canvas = tk.Canvas(
            root,
            width=self.display_w,
            height=self.display_h,
            highlightthickness=0,
            bg="#1a1a1a",
        )
        self.canvas.pack(side=tk.TOP, padx=6, pady=6)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo, tags="bg")

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        root.bind("<Control-s>", lambda e: self._save_to_desktop())
        root.bind("<Command-s>", lambda e: self._save_to_desktop())  # Mac

        # Done button
        tk.Button(
            root,
            text="Done",
            bg="#27ae60",
            fg="#ffffff",
            activebackground="#219a52",
            activeforeground="#ffffff",
            font=("", 11),
            padx=20,
            pady=6,
            relief=tk.FLAT,
            command=self._on_done,
        ).pack(side=tk.BOTTOM, pady=8)

    def _set_color(self, c):
        self.current_color = c

    def _set_tool(self, t):
        self.current_tool = t
        self._update_tool_buttons()

    def _update_tool_buttons(self):
        for name, btn in self._tool_btns.items():
            if name == self.current_tool:
                btn.configure(bg="#1abc9c", fg="#ffffff")
            else:
                btn.configure(bg="#34495e", fg="#1a1a1a")

    def _on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.current_tool == TOOL_BRUSH:
            self.brush_line = [(event.x, event.y)]
        else:
            self.current_item = self._create_shape_start(event.x, event.y)

    def _create_shape_start(self, x, y):
        if self.current_tool == TOOL_ARROW:
            return self.canvas.create_line(x, y, x, y, fill=self.current_color, width=LINE_WIDTH, arrow=tk.LAST, arrowshape=(12, 14, 6))
        if self.current_tool == TOOL_RECT:
            return self.canvas.create_rectangle(x, y, x, y, outline=self.current_color, width=LINE_WIDTH)
        if self.current_tool == TOOL_CIRCLE:
            return self.canvas.create_oval(x, y, x, y, outline=self.current_color, width=LINE_WIDTH)
        return None

    def _on_drag(self, event):
        if self.current_tool == TOOL_BRUSH:
            self.brush_line.append((event.x, event.y))
            if len(self.brush_line) >= 2:
                a, b = self.brush_line[-2], self.brush_line[-1]
                self.canvas.create_line(a[0], a[1], b[0], b[1], fill=self.current_color, width=BRUSH_WIDTH, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        elif self.current_item is not None:
            self._update_shape(self.current_item, self.start_x, self.start_y, event.x, event.y)

    def _update_shape(self, item, x0, y0, x1, y1):
        if self.current_tool == TOOL_ARROW:
            self.canvas.coords(item, x0, y0, x1, y1)
        elif self.current_tool == TOOL_RECT:
            self.canvas.coords(item, x0, y0, x1, y1)
        elif self.current_tool == TOOL_CIRCLE:
            self.canvas.coords(item, x0, y0, x1, y1)

    def _on_release(self, event):
        if self.current_tool != TOOL_BRUSH and self.current_item is not None:
            self._update_shape(self.current_item, self.start_x, self.start_y, event.x, event.y)
        self.current_item = None
        self.brush_line = []

    def _save_to_desktop(self):
        """Save the current canvas (image + annotations) to Desktop as PNG."""
        try:
            desktop = _desktop_path()
            os.makedirs(desktop, exist_ok=True)
            name = datetime.now().strftime("screencap_%Y-%m-%d_%H-%M-%S.png")
            path = os.path.join(desktop, name)
            # Grab canvas area in screen coordinates
            x = self.root.winfo_rootx() + self.canvas.winfo_x()
            y = self.root.winfo_rooty() + self.canvas.winfo_y()
            w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
            img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            img.save(path)
            self.root.title(f"Screencap – Saved to {name}")
        except Exception as e:
            self.root.title(f"Screencap – Save failed: {e}")

    def _on_done(self):
        self.root.destroy()


def _show_annotation_window(pil_image, parent_root=None):
    if parent_root is not None:
        win = tk.Toplevel(parent_root)
    else:
        win = tk.Tk()
    win.geometry(f"{min(pil_image.size[0], 1200)}x{min(pil_image.size[1], 800) + 120}")
    AnnotationWindow(win, pil_image)
    if parent_root is None:
        win.mainloop()


# --- Hotkey and main ---
def on_capture():
    try:
        full_img = capture_screen()
    except Exception as e:
        print("Capture failed:", e, file=sys.stderr)
        return
    root = getattr(on_capture, "_root", None)
    if root is None or not root.winfo_exists():
        root = None

    if root is not None:
        root.after(0, lambda: _show_region_then_annotate(full_img, root))
    else:
        _show_region_then_annotate(full_img, None)


def _show_region_then_annotate(full_image, parent_root):
    """Show region selector; on done, open annotation window with cropped image. Esc = cancel."""
    def on_region_done(cropped):
        if cropped is not None:
            _show_annotation_window(cropped, parent_root)

    if parent_root is None:
        parent_root = tk.Tk()
        parent_root.withdraw()
    RegionSelector(parent_root, full_image, on_region_done)


def main():
    root = tk.Tk()
    root.withdraw()  # hide main window
    on_capture._root = root

    # Menu bar (e.g. for dock icon / app menu on macOS)
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    capture_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Capture", menu=capture_menu)
    capture_menu.add_command(label="Capture screen", command=on_capture)

    hotkey_desc = "Ctrl+Cmd+3" if _IS_MAC else "Ctrl+Alt+3"
    print(f"Screencap running. Press {hotkey_desc} to capture. Ctrl+S in annotate window to save. Ctrl+C to exit.")

    def on_sigint(*_):
        root.after(0, root.quit)

    try:
        signal.signal(signal.SIGINT, on_sigint)
    except (ValueError, OSError):
        pass  # main thread only on some platforms

    def run_listener():
        with keyboard.GlobalHotKeys({HOTKEY: on_capture}):
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

    listener_thread = threading.Thread(target=run_listener, daemon=True)
    listener_thread.start()

    root.mainloop()


if __name__ == "__main__":
    main()
