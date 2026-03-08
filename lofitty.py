#!/usr/bin/env python3
import mpv
import pyperclip
import curses
import time
import random

STREAM_URL = "https://boxradio-edge-00.streamafrica.net/lofi"
track_history = []
current_track = "LoFi Stream"
player = mpv.MPV(ytdl=False, input_default_bindings=True)
player.play(STREAM_URL)
is_playing = True

MIN_WIDTH = 10  # tiny terminals now supported

def restart_stream():
    global player, is_playing
    try: player.quit()
    except: pass
    player = mpv.MPV(ytdl=False, input_default_bindings=True)
    player.play(STREAM_URL)
    is_playing = True

def toggle_play_pause():
    global is_playing
    player.pause = is_playing
    is_playing = not is_playing

def safe_addstr(stdscr, y, x, text, attr=0):
    """Draw string safely, ignore errors if terminal too small."""
    height, width = stdscr.getmaxyx()
    if y < height and x < width:
        try:
            stdscr.addstr(y, x, text[:max(0, width-x)], attr)
        except curses.error:
            pass

def main(stdscr):
    global current_track
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_MAGENTA, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_GREEN, -1)
    stdscr.nodelay(True)

    last_track = ""
    while True:
        # update track
        if player.metadata: current_track = player.metadata.get("icy-title", "LoFi Stream")
        else: current_track = "LoFi Stream"

        if current_track != last_track:
            last_track = current_track
            if not track_history or track_history[-1] != current_track:
                track_history.append(current_track)

        height, width = stdscr.getmaxyx()
        stdscr.clear()

        # Track display
        if width >= MIN_WIDTH:
            text = current_track[:width]
            x = max((width - len(text)) // 2, 0)
            for i, ch in enumerate(text):
                color = random.randint(1,3)
                attr = curses.color_pair(color)
                if random.random() < 0.3: attr |= curses.A_BOLD
                safe_addstr(stdscr, 0, x+i, ch, attr)

        # Visualizer if space allows
        bar_start = 2
        if height >= 4:
            for i in range(min(width, 20)):
                h = random.randint(0, max(1, height-4))
                for j in range(h):
                    safe_addstr(stdscr, bar_start + j, i, "|", curses.color_pair(4))

        # Status line
        status = "[P]" if is_playing else "[||]"
        status_line = f"{status} Enter=Copy Space=Play/Pause R=Restart"
        safe_addstr(stdscr, height-1, 0, status_line)

        stdscr.refresh()

        # Input
        try:
            key = stdscr.getkey()
            if key == "\n": pyperclip.copy(current_track)
            elif key.lower() == "r": restart_stream()
            elif key == " ": toggle_play_pause()
        except curses.error: pass

        time.sleep(0.2)

try:
    curses.wrapper(main)
except KeyboardInterrupt:
    print("\nExiting Lofitty...")
    print("Played tracks:")
    for t in track_history: print("-", t)
    player.quit()
