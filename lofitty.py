#!/usr/bin/env python3
"""
Lofitty - Terminal LoFi Radio Player
Glitchy interface, copy track, track history.
Handles small terminal windows gracefully.
"""

import mpv
import pyperclip
import curses
import time
import random

STREAM_URL = "https://boxradio-edge-00.streamafrica.net/lofi"

track_history = []
current_track = "LoFi Stream"

# Setup MPV player
player = mpv.MPV(ytdl=False, input_default_bindings=True)
player.play(STREAM_URL)

# Minimal terminal width required for interface
MIN_WIDTH = 30

def main(stdscr):
    global current_track

    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()

    # Define colors for glitch
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_MAGENTA, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)

    stdscr.nodelay(True)
    stdscr.clear()

    last_track = ""

    while True:
        # Get track safely
        if player.metadata is not None:
            current_track = player.metadata.get("icy-title") or "LoFi Stream"
        else:
            current_track = "LoFi Stream"

        # Update history
        if current_track != last_track:
            last_track = current_track
            if not track_history or track_history[-1] != current_track:
                track_history.append(current_track)

        # Get terminal size
        height, width = stdscr.getmaxyx()

        stdscr.clear()

        if width < MIN_WIDTH:
            # Terminal too small: show warning
            warning = "Terminal too small for interface"
            stdscr.addstr(0, 0, warning[:width-1])
        else:
            # Render glitchy interface
            text_to_draw = current_track[:width-1]  # truncate if needed
            x_start = max((width - len(text_to_draw)) // 2, 0)
            for i, ch in enumerate(text_to_draw):
                color = random.randint(1,3)
                attr = curses.color_pair(color)
                if random.random() < 0.3:
                    attr |= curses.A_BOLD
                try:
                    stdscr.addstr(0, x_start + i, ch, attr)
                except curses.error:
                    pass  # ignore if still out of bounds

            stdscr.addstr(2, 0, "Press Enter to copy track, Ctrl+C to exit"[:width-1])

        stdscr.refresh()

        # Handle Enter key
        try:
            key = stdscr.getkey()
            if key == "\n" and width >= MIN_WIDTH:
                pyperclip.copy(current_track)
                msg = f"Copied: {current_track}"
                stdscr.addstr(4, 0, msg[:width-1])
        except curses.error:
            pass  # no key pressed

        time.sleep(0.3)

try:
    curses.wrapper(main)
except KeyboardInterrupt:
    print("\nExiting Lofitty...")
    print("Played tracks:")
    for t in track_history:
        print("-", t)
    player.quit()
