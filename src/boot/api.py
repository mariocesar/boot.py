import json
import os
import pathlib
import shlex
import subprocess
import sys
from collections.abc import MutableMapping
from contextlib import contextmanager
from urllib.request import urlopen

from boot.facts import FactFile
from boot.utils import sha1sum
from .types import Color, RunResult

assert sys.version_info >= (3, 6), "This projects needs python3.6 or greater"

__all__ = ['echo', 'abort', 'warn', 'indent', 'step', 'run', 'task', 'Task']

VERBOSE_DEFAULT = os.environ.get('BOOT_PY_VERBOSE', 0)

assert isinstance(VERBOSE_DEFAULT, int)


def echo(message: str, end='\n'):
    sys.stdout.write(message + end)
    sys.stdout.flush()


def abort(message: str):
    sys.stderr.write(f'\n{Color.red}Fatal Error: {Color.bold}{message}{Color.reset}\n')
    sys.stderr.write(f'\n{Color.red}Aborting.{Color.reset}\n')
    sys.stderr.flush()


def warn(message: str):
    sys.stderr.write(f'\n{Color.yellow}Warning: {Color.bold}{message}{Color.reset}\n')
    sys.stderr.flush()


@contextmanager
def indent(prefix='    '):
    """Indent the message given"""
    old_write = sys.stdout.write
    _prefix = f'{prefix}{{}}'.format

    def write(val):
        for line in val.split('\n'):
            old_write(_prefix(line))
            old_write('\n')
            sys.stdout.flush()

    sys.stdout.write = write

    yield

    sys.stdout.write = old_write


@contextmanager
def withenv(**kwargs):
    """Temporary override the os.environ values."""

    old_values = {}
    prune = []

    for name, value in kwargs.items():
        if name in os.environ:
            old_values[name] = os.environ.get(name)
        else:
            prune.append(name)
        os.environ[name] = value

    try:
        yield
    finally:
        for name in prune:
            del os.environ[name]

        for name, value in old_values:
            os.environ[name] = value


def prompt(spec_path: str):
    """Ask for values defined in a json file"""

    path = pathlib.Path(spec_path).resolve()

    try:
        spec = json.loads(open(path, 'rt'))
    except json.JSONDecodeError:
        raise ValueError('Unable to parse the variables specs.')

    if not isinstance(spec, dict):
        raise ValueError(f'Expected a key, value object. got type {type(spec)}')

    for key in spec:
        val = spec[key]

        if val is not None and not isinstance(spec[key], (str, float, bool, int)):
            raise ValueError(f'Unsupported spec value for {key}: type {type(spec)}')

    values = {}

    for key in spec:
        values[key] = input(f'{key} {spec[key]}: ')

    return values


def urlfetch(url: str, dest=None):
    """Fetch an url, returns the output or write to `dest`"""

    response = urlopen(url)

    if dest:
        with open(dest, 'wb') as fb:
            fb.write(response.read())
        return fb
    else:
        return response.read()


@contextmanager
def step(message: str):
    echo(message, end='')
    echo(' ... ', end='')

    try:
        yield
    except Exception as err:
        echo(f'{Color.bold_red}[Error]{Color.reset}')

        if hasattr(err, 'message'):
            echo(f'{err.message}')
        else:
            echo(f'{err!r}')
    else:
        echo(f'{Color.bold_green}[Ok]{Color.reset}')


@contextmanager
def cd(path: str):
    """Switch the working directory within the context"""

    old = os.getcwd()
    os.chdir(path)

    try:
        yield
    finally:
        os.chdir(old)


def run(command: str, verbose: int = VERBOSE_DEFAULT, silent: bool = False) -> RunResult:
    """Run a shell command, returns the output and exitcode"""
    if verbose > 0:
        echo(f' > {command}')

    proc = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (stdout, stderr) = proc.communicate()

    ret = RunResult(stdout.decode(), stderr.decode(), proc.returncode)

    if not (silent or ret.ok):
        with indent(' < '):
            echo(ret.out)
            echo(ret.err)
        exit(1)

    if verbose > 1:
        with indent(' < '):
            echo(ret.out)
            if ret.err.strip():
                echo(ret.err)

    return ret


class Task(MutableMapping):
    __slots__ = ['_queue', '_context', '__doc__', '_facts']

    def __init__(self, func, *args):
        self._context = {}
        self._queue = []
        self._queue.append(func)
        self._facts = None

    @property
    def facts(self):
        if self._facts is None:
            self._facts = FactFile('facts.json')

        return self._facts

    def __getitem__(self, key):
        return self._context[key]

    def __setitem__(self, key, value):
        self._context[key] = value

    def __delitem__(self, key):
        del self._context[key]

    def __iter__(self):
        return iter(self._context)

    def __len__(self):
        return len(self._queue)

    def __rshift__(self, other):
        if isinstance(other, Task):
            self._queue.extend(other._queue)
        else:
            self._queue.append(other)
        return self

    def __call__(self, *args, **kwargs):
        self.facts.checkout()

        for func in self._queue:
            func(self)

        self.facts.commit()

        return self

    def file_changed(self, path):
        if 'sha1sums' not in self.facts:
            self.facts['sha1sums'] = {}

        new_sum = sha1sum(path)

        if path in self.facts['sha1sums']:
            if new_sum == self.facts['sha1sums'][path]:
                return False

        self.facts['sha1sums'][path] = new_sum

        return True


def task(func):
    inner = Task(func)
    setattr(inner, '__doc__', func.__doc__)
    return inner
