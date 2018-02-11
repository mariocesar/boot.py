#!/usr/bin/env python3
import os
import shlex
import subprocess
import sys
import pathlib
import json

from urllib.request import urlopen
from collections import namedtuple
from contextlib import contextmanager

assert sys.version_info >= (3, 6), "This projects needs python3.6 or greater"

os.environ['LANG'] = 'C'

__all__ = ['Color', 'echo', 'abort', 'warn', 'indent', 'step', 'run']


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


def echo(message, out=sys.stdout):
    out.write(message)
    out.flush()


def abort(message: str):
    sys.stderr.write(f'\n{Color.red}Fatal Error: {Color.bold}{message}{Color.reset}\n')
    sys.stderr.write(f'\n{Color.red}Aborting.{Color.reset}\n')
    sys.stderr.flush()


def warn(message: str):
    sys.stderr.write(f'\n{Color.yellow}Warning: {Color.bold}{message}{Color.reset}\n')
    sys.stderr.flush()


def indent(message: str, out=sys.stdout):
    for line in message.strip().split('\n'):
        out.write(f'    {line}\n')
        out.flush()


def prompt(spec_path: str):
    path = pathlib.Path(spec_path).resolve()

    try:
        spec = json.loads(open(path, 'rt'))
    except json.JSONDecodeError:
        raise ValueError('Unable to parse the variables specs.')

    if not isinstance(spec, dict):
        raise ValueError(f'Expected a key, value object. got type {type(spec)}')

    for key in spec:
        if not isinstance(spec[key], (str, float, bool, int, None)):
            raise ValueError(f'Unsupported spec value for {key}: type {type(spec)}')

    values = {}

    for key in spec:
        values[key] = input(f'{key} {spec[key]}: ')

    return values


def urlfetch(url: str, dest=None):
    response = urlopen(url)

    if dest:
        with open(dest, 'wb') as fb:
            fb.write(response.read())
        return fb
    else:
        return response.read()


@contextmanager
def step(*args, **kwargs):
    echo(*args, **kwargs)
    echo(' ... ')

    try:
        yield
    except AssertionError as err:
        echo(f' {Color.red}[Failed]{Color.reset}\nError: {err!s}\n')
        sys.exit(1)
    except Exception as err:
        echo(f' {Color.red}[Failed]{Color.reset}\n')
        echo(repr(err))
        sys.exit(1)
    else:
        echo(f' {Color.bold + Color.green}[Ok]{Color.reset}\n')


RunResult = namedtuple('RunResult', 'out,exitcode')


def run(command: str):
    proc = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (stdout, stderr) = proc.communicate()

    return RunResult(stdout.decode(), proc.returncode)
