#!/usr/bin/env python3
# Lofitty — Console TUI (curses) with single-key controls and station manager
# - SPACE: play/pause
# - ← / →  or p / n : prev / next station
# - ENTER: copy current track to clipboard
# - a: add station
# - r: remove current station
# - s: save stations
# - h: toggle history panel
# - q: quit
#
# Saves stations to ~/.config/lofitty/stations.json
# Requires: python-mpv, pyperclip

# ---- Locale fix: must be before importing mpv ----
import os
os.environ.setdefault("LC_ALL", "C")
os.environ.setdefault("LC_NUMERIC", "C")
import locale
try:
    locale.setlocale(locale.LC_NUMERIC, "C")
except Exception:
    pass

import threading
import time
import json
from pathlib import Path

# Import mpv after locale fix
import mpv
import pyperclip

# curses import (may fail on some platforms)
try:
    import curses
    CURSES_OK = True
except Exception:
    CURSES_OK = False

# config
CONFIG_DIR = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / "lofitty"
STATIONS_FILE = CONFIG_DIR / "stations.json"
DEFAULT_STREAM = "https://boxradio-edge-00.streamafrica.net/lofi"

def load_stations():
    try:
        if STATIONS_FILE.exists():
            with open(STATIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and data:
                    return data
    except Exception:
        pass
    return [{"name": "LoFi", "genre": "LoFi", "url": DEFAULT_STREAM}]

def save_stations(stations):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(stations, f, ensure_ascii=False, indent=2)

# ---- Core player + shared state ----
class PlayerState:
    def __init__(self):
        self.stations = load_stations()
        if not self.stations:
            self.stations = [{"name": "LoFi", "genre": "LoFi", "url": DEFAULT_STREAM}]
        self.idx = 0
        self.current_track = "LoFi Stream"
        self.history = []
        self.playing = True
        self.quit = False
        self.show_history = False
        self.lock = threading.Lock()
        # mpv player
        self.player = mpv.MPV(ytdl=False)
        # start playing first station safely
        try:
            self.player.play(self.stations[self.idx]["url"])
        except Exception:
            pass

    def play_station(self, idx):
        with self.lock:
            if idx < 0 or idx >= len(self.stations): return
            self.idx = idx
            try:
                self.player.play(self.stations[self.idx]["url"])
            except Exception:
                pass
            self.playing = True

    def toggle_play(self):
        with self.lock:
            try:
                self.player.pause = self.playing
            except Exception:
                pass
            self.playing = not self.playing

    def next_station(self):
        with self.lock:
            self.idx = (self.idx + 1) % max(1, len(self.stations))
            try:
                self.player.play(self.stations[self.idx]["url"])
            except Exception:
                pass
            self.playing = True

    def prev_station(self):
        with self.lock:
            self.idx = (self.idx - 1) % max(1, len(self.stations))
            try:
                self.player.play(self.stations[self.idx]["url"])
            except Exception:
                pass
            self.playing = True

    def add_station(self, name, genre, url):
        with self.lock:
            self.stations.append({"name": name, "genre": genre, "url": url})

    def remove_current_station(self):
        with self.lock:
            if len(self.stations) <= 1:
                return False
            removed = self.stations.pop(self.idx)
            # clamp index
            self.idx = min(self.idx, len(self.stations)-1)
            try:
                self.player.play(self.stations[self.idx]["url"])
            except Exception:
                pass
            return True

    def shutdown(self):
        try:
            self.player.quit()
        except Exception:
            pass

# metadata updater thread
def metadata_thread(state: PlayerState):
    while not state.quit:
        try:
            meta = state.player.metadata
            if meta:
                title = meta.get("icy-title", None)
                if title:
                    with state.lock:
                        if title != state.current_track:
                            state.current_track = title
                            state.history.insert(0, title)
        except Exception:
            pass
        time.sleep(0.9)

# ---- nice text helpers ----
def trim(text, width):
    if len(text) <= width: return text
    if width <= 3: return text[:width]
    return text[:width-3] + "..."

# ---- curses UI ----
def curses_main(stdscr, state: PlayerState):
    curses.curs_set(0)
    stdscr.nodelay(True)   # non-blocking getch
    stdscr.keypad(True)
    height, width = stdscr.getmaxyx()

    # Colors
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)   # header
        curses.init_pair(2, curses.COLOR_CYAN, -1)  # accent text
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE) # status bar
        curses.init_pair(4, curses.COLOR_YELLOW, -1) # track
        curses.init_pair(5, curses.COLOR_GREEN, -1) # playing

    def draw():
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        # Header
        header = " Lofitty — Console Player "
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(0, 0, " " * w)
        stdscr.addstr(0, max(0, (w - len(header))//2), header)
        stdscr.attroff(curses.color_pair(1))

        # Current station & status
        with state.lock:
            station = state.stations[state.idx]
            playing = state.playing
            track = state.current_track

        status = "Playing" if playing else "Paused"
        status_col = curses.color_pair(5) if playing else curses.A_DIM
        st_line = f"[{state.idx}] {station['name']}  ({station.get('genre','')})  — {status}"
        stdscr.addstr(2, 2, trim(st_line, w-4), status_col)

        # Current track
        stdscr.addstr(4, 2, "Track: ", curses.color_pair(4) | curses.A_BOLD)
        stdscr.addstr(4, 9, trim(track, w-12))

        # Station list (left)
        stdscr.addstr(6, 2, "Stations:", curses.A_UNDERLINE)
        max_list_h = h - 14
        start_y = 7
        for i, s in enumerate(state.stations[:max_list_h]):
            marker = ">" if i == state.idx else " "
            line = f" {marker} [{i}] {s['name']} ({s.get('genre','')})"
            if i == state.idx:
                stdscr.addstr(start_y + i, 2, trim(line, w-4), curses.A_REVERSE)
            else:
                stdscr.addstr(start_y + i, 2, trim(line, w-4))

        # History box (right)
        hist_x = max(40, w//2)
        stdscr.addstr(6, hist_x, "History:", curses.A_UNDERLINE)
        max_hist_h = h - 14
        for i, t in enumerate(state.history[:max_hist_h]):
            stdscr.addstr(7 + i, hist_x, trim(f"- {t}", w - hist_x - 2))

        # Status / hints bar at bottom
        hint = "SPACE:Play/Pause  ←/→:Prev/Next  ENTER:CopyTrack  a:Add  r:Remove  s:Save  h:ToggleHistory  q:Quit"
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(h-2, 0, " " * w)
        stdscr.addstr(h-2, 1, trim(hint, w-2))
        stdscr.attroff(curses.color_pair(3))

        # If history toggle is off, show small notice
        if not state.show_history:
            stdscr.addstr(h-4, 2, "(press 'h' to show full history)", curses.A_DIM)

        stdscr.refresh()

    # Main loop: poll keys, redraw
    draw()
    while not state.quit:
        try:
            ch = stdscr.getch()
        except Exception:
            ch = -1
        if ch != -1:
            # handle keys
            if ch in (ord('q'), ord('Q')):
                state.quit = True
                break
            elif ch in (ord(' '),):
                state.toggle_play()
            elif ch in (curses.KEY_RIGHT, ord('n'), ord('N')):
                state.next_station()
            elif ch in (curses.KEY_LEFT, ord('p'), ord('P')):
                state.prev_station()
            elif ch in (ord('\n'), curses.KEY_ENTER, 10, 13):
                # copy current track
                with state.lock:
                    pyperclip.copy(state.current_track)
                # flash small message
                stdscr.addstr(4, 9, "Copied!"+ " " * (width-20), curses.A_BOLD)
                stdscr.refresh()
                time.sleep(0.25)
            elif ch in (ord('s'), ord('S')):
                save_stations(state.stations)
            elif ch in (ord('r'), ord('R')):
                ok = state.remove_current_station()
                if not ok:
                    # flash cannot remove
                    stdscr.addstr(2, 2, "Cannot remove last station!", curses.A_BOLD)
                    stdscr.refresh()
                    time.sleep(0.6)
            elif ch in (ord('a'), ord('A')):
                # Add station: switch to blocking input mode
                curses.curs_set(1)
                stdscr.nodelay(False)
                stdscr.addstr(height-4, 2, "Add station - name: " + " " * (width-30))
                stdscr.move(height-4, 24)
                curses.echo()
                try:
                    name = stdscr.getstr().decode('utf-8').strip()
                except Exception:
                    name = ""
                stdscr.addstr(height-3, 2, "Genre: " + " " * (width-20))
                stdscr.move(height-3, 9)
                try:
                    genre = stdscr.getstr().decode('utf-8').strip()
                except Exception:
                    genre = ""
                stdscr.addstr(height-2, 2, "URL: " + " " * (width-20))
                stdscr.move(height-2, 6)
                try:
                    url = stdscr.getstr().decode('utf-8').strip()
                except Exception:
                    url = ""
                curses.noecho()
                stdscr.nodelay(True)
                curses.curs_set(0)
                # cleanup input lines
                for i in range(4):
                    stdscr.move(height-4 + i, 0)
                    stdscr.clrtoeol()
                if name and url:
                    state.add_station(name, genre or "Unknown", url)
                draw()
            elif ch in (ord('h'), ord('H')):
                state.show_history = not state.show_history
                # if show_history true, open a full-page simple history view
                if state.show_history:
                    show_history_screen(stdscr, state)
                draw()

            # redraw after handling key
            draw()
        else:
            # no key: redraw periodically
            draw()
            time.sleep(0.05)

    # finishing
    state.shutdown()

def show_history_screen(stdscr, state: PlayerState):
    # full screen history viewer: press any key to go back
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    title = " History (press any key to return) "
    stdscr.addstr(0, max(0,(w-len(title))//2), title, curses.A_REVERSE)
    with state.lock:
        items = state.history.copy()
    for i, t in enumerate(items[:h-4]):
        stdscr.addstr(2+i, 2, trim(f"{i+1}. {t}", w-4))
    stdscr.refresh()
    stdscr.nodelay(False)
    stdscr.getch()
    stdscr.nodelay(True)

# ---- fallback simple mode if curses not available ----
def simple_fallback():
    print("Curses not available. Running simple console Lofitty.")
    state = PlayerState = PlayerStateDummy()

# (not used; keeping code lean)

# ---- Entrypoint ----
def main():
    state = PlayerState()
    # metadata thread
    t = threading.Thread(target=metadata_thread, args=(state,), daemon=True)
    t.start()
    if CURSES_OK:
        curses.wrapper(curses_main, state)
    else:
        # fallback - basic loop (blocking input)
        print("curses not available on this system. Using simple mode.")
        try:
            while not state.quit:
                cmd = input("> ")
                if cmd.strip().lower() == "q":
                    state.quit = True
                    break
        except KeyboardInterrupt:
            state.quit = True
    # save stations on exit
    save_stations(state.stations)
    print("Exiting. Played tracks:")
    for h in state.history:
        print("-", h)

if __name__ == "__main__":
    main()
