# Screencap – Cross-platform screenshot + annotate

Capture the screen with **Ctrl+Cmd+3** (Mac) or **Ctrl+Alt+3** (Windows/Linux), then annotate with colors and shapes. **Ctrl+S** saves to Desktop; **Ctrl+C** exits.

## Requirements

- Python 3.7+
- macOS, Ubuntu (or most Linux), or Windows

## Install

From PyPI:

```bash
pip install python-cap
```

From source:

```bash
pip install -r requirements.txt
```

## Run

```bash
python-cap
```

Or from source: `python python-cap.py`

Leave the terminal open. Press **Ctrl+Cmd+3** (Mac) or **Ctrl+Alt+3** (Windows/Linux) to take a full-screen capture. The annotation window opens with:

- **6 colors** – red, blue, green, black, yellow, purple
- **Arrow** – draw an arrow (drag from start to end)
- **Rect** – rectangle
- **Circle** – circle/oval
- **Brush** – freehand drawing

- **Ctrl+S** (or **Cmd+S** on Mac) – save the annotated image to your Desktop as PNG.
- Click **Done** to close the annotation window. The app keeps running; use the hotkey again to capture another screen.
- **Ctrl+C** in the terminal stops the program.

## Permissions

- **macOS**: Allow the terminal (or Python) in **System Settings → Privacy & Security → Accessibility** so the global hotkey works.
- **Linux**: Some setups need accessibility or input-monitor permissions for global hotkeys.
- **Windows**: No extra steps usually needed.

## Publishing to PyPI

1. Create an account at [pypi.org](https://pypi.org) and create a [token](https://pypi.org/manage/account/token/) (scope: entire account or just this project).
2. Install build and twine: `pip install build twine`
3. From the project root: `python -m build`
4. Upload: `twine upload dist/*` (use `__token__` as username and your token as password, or set `TWINE_USERNAME` / `TWINE_PASSWORD`).
5. If the name `python-cap` is taken on PyPI, change `name` in `pyproject.toml` to something unique (e.g. `screencap-app`) and rebuild.
