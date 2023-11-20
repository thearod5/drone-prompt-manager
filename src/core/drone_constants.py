import os

from prompts.prompt_args import PromptArgs

"""
Lists all the constants used throughout the project.
"""
DRONE_KEY = "drone"
DRONE_ID_KEY = "id"
STATION_KEY = "station"
CELLS_KEY = "cells"
PROMPY_KEY = "prompt"
COMPLETION_KEY = "completion"
n_width_blocks = 14
n_height_blocks = 8
cells_in_single_battery = 3
battery_time = 30  # minutes
BlockCoordinate = str
NEW_LINE = os.linesep
DronePromptArgs = PromptArgs(prompt_prefix="", prompt_suffix="\n>", completion_prefix="", completion_suffix="")
NEW_LINE = os.linesep
SPACE = " "
EMPTY_STRING = ''
TAB = "\t"
PERIOD = "."
COMMA = ","
UNDERSCORE = "_"
F_SLASH = "/"
B_SLASH = "\\"
SEMI_COLON = ";"
BRACKET_OPEN = "{"
BRACKET_CLOSE = "}"
DASH = "-"
COLON = ":"
L_CARROT = "<"
R_CARROT = ">"
L_BRACKET = "["
R_BRACKET = "]"
