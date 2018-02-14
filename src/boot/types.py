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


RunResult = namedtuple('RunResult', 'out,exitcode')
