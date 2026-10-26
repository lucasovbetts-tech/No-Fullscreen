# win-toolbox

Windows utility that detects when a browser enters fullscreen and instantly exits it.

## How it works
- Uses Win32 event hooks (`SetWinEventHook`) to get notified the moment a window changes size or focus — no polling.
- If the focused window belongs to a browser and exactly matches the monitor's size, it sends **F11** to exit fullscreen.
- Maximised windows are ignored.

Supported browsers: Chrome, Edge, Firefox, Brave, Opera, Vivaldi.

## Requirements
- Windows
- Python 3 (no extra packages)

## Usage
```
python no_fullscreen.py
```
Close the terminal to stop it.

To run hidden on startup, rename to `no_fullscreen.pyw` and put a shortcut in `shell:startup`.

## Why I made this
- My college uses uplearn that automatically goes into fullscreen a lot which I didn't like
  so I made this to automatically exit fullscreen.
