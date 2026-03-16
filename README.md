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
python_cap
```

Or from source: `python python_cap.py`

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

1. **Account & token**  
   Create an account at [pypi.org](https://pypi.org) and create an [API token](https://pypi.org/manage/account/token/) (scope: entire account or project-specific).

2. **Install build tools** (one-time):
   ```bash
   pip install build twine
   ```

3. **Bump version** (optional)  
   Edit `version` in `pyproject.toml` (e.g. `0.1.1`) before each release.

4. **Build** (from project root):
   ```bash
   rm -rf dist build *.egg-info
   python -m build
   ```

5. **Upload**:
   ```bash
   twine upload dist/*
   ```
   When prompted:
   - Username: `__token__`
   - Password: your PyPI API token  

   Or use env vars (no prompt):
   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-YourTokenHere
   twine upload dist/*
   ```

6. **Test install** (optional):
   ```bash
   pip install python-cap --force-reinstall
   python-cap
   ```

If the name `python-cap` is taken on PyPI, change `name` in `pyproject.toml` to a unique name, then rebuild and upload again.
