import csv
import time
import os
import numpy as np
import simpleaudio as sa
import math
import sys
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON


FILE = "flight_of_the_bumblebee.mid"

# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.
port = sys.argv[1] if len(sys.argv) > 1 else None

try:
    midiout, port_name = open_midioutput(port)
except (EOFError, KeyboardInterrupt):
    sys.exit()


def note_on(note):
    note_on = [NOTE_ON, note, 127]  # channel 1, middle C, velocity 112
    midiout.send_message(note_on)


def note_off(note):
    note_off = [NOTE_OFF, note, 0]
    midiout.send_message(note_off)

def it(style, text: str, background: int = None) -> str:
    """
    format string w/ escape sequence to a specific color "style":
       ~ RGB as tuple(red, green, blue)
       ~ HEX prefixed with # as #EEEEEE
       ~ integer 256 color
       ~ or one of ten named color "emphasis" strings from the 256 pallette
    background needs to an integer 256 color
    Credit: litepresence.com
    """

    def hex_to_rgb(value):
        value = value.lstrip("#")
        lenv = len(value)
        return tuple(
            int(value[i : i + lenv // 3], 16) for i in range(0, lenv, lenv // 3)
        )

    # monokai
    emphasis = {
        "red": 197,
        "green": 154,
        "yellow": 227,
        "orange": 208,
        "purple": 141,
        "blue": 51,
        "white": 231,
        "gray": 250,
        "grey": 250,
        "black": 236,
        "cyan": 51,
    }
    ret = text
    if background is not None:
        text = f"\033[48;5;{background}m" + str(text)
    if isinstance(style, str):
        if style[0] == "#":
            style = hex_to_rgb(style)
            red, green, blue = style
            ret = f"\033[38;2;{red};{green};{blue}m" + str(text) + "\033[0m"
        else:
            ret = f"\033[38;5;{emphasis[style]}m" + str(text) + "\033[0m"
    elif isinstance(style, int):
        ret = f"\033[38;5;{style}m" + str(text) + "\033[0m"
    elif isinstance(style, tuple):
        red, green, blue = style
        ret = f"\033[38;2;{red};{green};{blue}m" + str(text) + "\033[0m"
    return ret


WIDTH = 127
HEIGHT = 50

print("\033c")

os.system(f"midicsv '{FILE}' output.csv")

with open("output.csv") as csvfile:
    data = list(csv.reader(csvfile))
    csvfile.close()

SPEED = int(data[0][5])*2

data2 = []
for i in data:
    if "Note" in i[2]:
        inner = []
        inner.append(int(i[0]))  # track
        inner.append(int(i[1]))  # time
        inner.append(i[2].replace(" Note_", "").replace("_c", ""))  # on off
        inner.append(int(i[4]))  # note
        data2.append(inner)

maxl = max([int(i[1]) for i in data2])
data2 = sorted(data2, key=lambda x: x[1])
notes = []
frames = {
    0: (((" " * 127) + "\n") * HEIGHT),
    **{i[1]: (((" " * 127) + "\n") * HEIGHT) for i in data2},
}


print("Generating...")

for idx, event in enumerate(data2[:300]):
    if idx - int(0) >= 0:
        e = data2[idx - 0]
    else:
        e = [0, data2[idx][1], 0, -1]
    try:
        notes.append([int(e[0]), e[1], str(e[2]).replace(" ", ""), e[3]])
    except Exception as e:
        print(e)
    frames[event[1]] = [[c for c in i] for i in frames[event[1]].split("\n")]
    times = [i[1] for i in data2]
    idx = times.index(event[1]) - 1
    for i in range(HEIGHT, 3, -1):
        try:
            frames[event[1]][i] = [
                [c for c in i]
                for i in frames[times[idx]].split("\n")
            ][i - 2]
        except Exception as e:
            print(e)
        # print(idx, i)
    # print(frames[idx])
    frames[event[1]][2][int(event[3])] = "█"
    frames[event[1]][HEIGHT - 4] = (
        it("white", "█")
        + it("black", "█")
        + it("white", "█")
        + it("black", "█")
        + it("white", "█")
        + it("white", "█")
        + it("black", "█")
        + it("white", "█")
        + it("black", "█")
        + it("white", "█")
        + it("black", "█")
        + it("white", "█")
    ) * int(127 / 12) + (
        it("white", "█")
        + it("black", "█")
        + it("white", "█")
        + it("black", "█")
        + it("white", "█")
        + it("white", "█")
    )
    frames[event[1]][HEIGHT - 3] = frames[event[1]][HEIGHT - 4]
    frames[event[1]][HEIGHT - 2] = frames[event[1]][HEIGHT - 3]
    frames[event[1]][HEIGHT - 1] = it("white", "█") * 126
    frames[event[1]][HEIGHT] = frames[event[1]][HEIGHT - 1]
    frames[event[1]] = "\n".join(["".join(i) for i in frames[event[1]]])
    # print("\033c")
    # print(frames[event[1]])
    # time.sleep(0.1)


input("Press enter to play.")

start = time.time() * SPEED
for idx, event in enumerate(notes):
    # print(notes[idx])
    # time.sleep(0.1)
    while time.time() * SPEED - start < event[1]:
        time.sleep(0.00001)
    print("\033c")
    print(frames[event[1]])
    if event[3] != -1:
        if event[2] == "on":
            note_on(float(event[3]))
        else:
            note_off(float(event[3]))
    else:
        time.sleep(0.1)
    # for n in note:
    #     play_note(cal_hz(float(n[0])), 1/0.1)
