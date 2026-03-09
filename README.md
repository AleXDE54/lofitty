# Lofitty

**Lofitty** is a minimal terminal-based LoFi radio player for Linux with a glitchy, dynamic interface.  
It plays a LoFi stream, shows the current track name, allows copying it to the clipboard, and keeps a history of all played tracks.

## Features

- Plays LoFi radio stream directly using [`mpv`](https://mpv.io/)  
- Terminal-based “glitchy” interface with colored text  
- Press **Enter** → copies the current track name to clipboard  
- Track history displayed on exit  
- **Terminal-resilient**: if your terminal is too small, shows a warning instead of crashing  

## Requirements

- Python 3.10+  
- [mpv](https://mpv.io/) installed system-wide  
- Python libraries:  
```bash
pip install python-mpv pyperclip
```
 - Linux terminal (supports curses)

# Installation

## Simple install:

Download my package manager from this [github](https://github.com/AleXDE54/realtools/tree/main)

```bash
rtls install AleXDE54/lofitty
```

## Manual install:

Clone the repository:
```bash
git clone https://github.com/AleXDE54/lofitty
cd lofitty
```

Install Python dependencies:

```bash
pip install --user python-mpv pyperclip
```

Run the player:

```bash
python lofitty.py
```

OR build it)

```bash
pyinstaller --onefile lofitty --name lofitty
```

aand clone it to path

```
cp lofitty /usr/local/bin/lofitty
```

# Usage

```
lofitty
```

# Notes
Works best on terminals that support colors and transparency (like Foot, Alacritty, Kitty, etc.)
