# Screencap – Cross-platform screenshot + annotate

Capture the screen with **Cmd+R** (Mac) or **Win+R** (Windows/Linux), then annotate with colors and shapes.

## Requirements

- Python 3.7+
- macOS, Ubuntu (or most Linux), or Windows

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python screencap.py
```

Leave the terminal open. Press **Cmd+R** (Mac) or **Win+R** (Windows/Linux) to take a full-screen capture. The annotation window opens with:

- **6 colors** – red, blue, green, black, yellow, purple
- **Arrow** – draw an arrow (drag from start to end)
- **Rect** – rectangle
- **Circle** – circle/oval
- **Brush** – freehand drawing

Click **Done** to close the annotation window. The app keeps running; use the hotkey again to capture another screen.

## Permissions

- **macOS**: Allow the terminal (or Python) in **System Settings → Privacy & Security → Accessibility** so the global hotkey works.
- **Linux**: Some setups need accessibility or input-monitor permissions for global hotkeys.
- **Windows**: No extra steps usually needed.
