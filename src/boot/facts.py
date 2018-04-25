import json
import os
import shutil
import time
from collections import MutableMapping
from copy import deepcopy
from json import JSONDecodeError
from pathlib import Path
from tempfile import mkstemp


class FactFile(MutableMapping):
    _state = None
    _data = None
    _path = None

    def __init__(self, path):
        self._path = Path(path)

        if not self._path.exists():
            self._path.touch(0o600)
            self._path.write_text('{}')

        self.checkout()

    def checkout(self):
        try:
            _data = json.loads(self._path.read_text())
        except (JSONDecodeError, TypeError):
            raise TypeError('Invalid content for fact file, expected json serialized.')

        if not isinstance(_data, dict):
            raise ValueError(f'Fact file is incorrect, expected an object not: {_data!r}')

        self._data = deepcopy(_data)
        self._state = deepcopy(_data)

    def commit(self):
        """Atomic save"""
        if self._state == self._data:
            # If there is no updates don't commit
            return

        fd, tmpname = mkstemp(text='b')

        self._state['last_commit'] = time.time()

        fobj = os.fdopen(fd, 'w')
        json.dump(self._state, fobj, indent=4)
        fobj.close()

        shutil.move(tmpname, str(self._path))

        self._path.chmod(0o600)

        self._data = deepcopy(self._state)
        self._state = None

    def save(self):
        self.commit()
        self.checkout()

    def __iter__(self):
        return iter(self._state)

    def __len__(self):
        return len(self._state)

    def __delitem__(self, key):
        del self._state[key]

    def __setitem__(self, key, value):
        self._state[key] = value

    def __getitem__(self, key):
        return self._state[key]


factfile = FactFile
