from collections import namedtuple


class Color:
    red = '\033[31m'
    green = '\033[32m'
    yellow = '\033[33m'
    blue = '\033[34m'
    magenta = '\033[35m'
    cyan = '\033[36m'
    gray = '\033[37m'

    bold = '\033[1m'
    underline = '\033[4m'
    reset = '\033[0m'

    bold_red = bold + red
    bold_green = bold + green
    bold_yellow = bold + yellow
    bold_blue = bold + blue
    bold_magenta = bold + magenta
    bold_cyan = bold + cyan
    bold_gray = bold + gray


RunResult = namedtuple('RunResult', 'out,exitcode')
TasksCliResult = namedtuple('TasksCliResult', 'parser,run')
