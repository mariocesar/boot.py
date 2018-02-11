Boot.py is a set of tools to build simple scripts.


Install and Use
---------------

Install simple by.::

pip install boot.py
::

Create a file and import `boot`. For example this, will install a virtual
environment, install requirements, and create some files.::

#!/usr/bin/env python3
import os
import venv

from pathlib import Path

root_path = Path(__file__).parent.resolve()
venv_dir = root_path / '.venv'


with step(f'Creating virtualenv in {venv_dir.name}'):
    if not venv_dir.exists():
        venv.create(venv_dir, with_pip=True)

    pip_bin = venv_dir / 'bin/pip'

    if not pip_bin.exists():
        raise RuntimeError('Virtualenv has no pip')


with step('Installing requirements'):
    run(f'{venv_dir / "bin/pip"} install -r requirements.txt')


with step('Creating directories ... '):
    run(f'mkdir -p public/media')
    run(f'mkdir -p public/static')


with step('Environment file'):
    envfile = root_path / '.env'

    if not envfile.exists():
        with open(envfile, 'w') as handle:
            os.chmod(envfile, 0o600)
            handle.write('')
::