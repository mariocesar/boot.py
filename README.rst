Boot.py is an small set of tools to build simple scripts. Python3 only, and really small: 2Kb!

.. image:: https://badge.fury.io/py/boot.py.svg
    :target: https://pypi.python.org/pypi/boot.py/

.. image:: https://travis-ci.org/mariocesar/boot.py.svg?branch=master
    :target: https://travis-ci.org/mariocesar/boot.py

Install and Use
---------------

Install with pip.

.. code-block:: console

    pip install boot.py


Create a file and import `boot`. For example this will install a virtual
environment, install requirements, and create some files.

.. code-block:: python

    #!/usr/bin/env python3
    import os
    import venv

    from boot import step, run
    from pathlib import Path

    root_path = Path(__file__).parent.resolve()
    venv_dir = root_path / '.venv'

    with step(f'Creating virtualenv in {venv_dir.name}'):
        if not venv_dir.exists():
            venv.create(venv_dir, with_pip=True)

    with step('Installing requirements'):
        run(f'{venv_dir / "bin/pip"} install -r requirements.txt')

    with step('Creating directories'):
        run(f'mkdir -p public/media')
        run(f'mkdir -p public/static')

    with step('Environment file'):
        envfile = root_path / '.env'

        if not envfile.exists():
            with open(envfile, 'w') as handle:
                os.chmod(envfile, 0o600)
                handle.write('')

This will output.

.. code-block:: console

    $ ./script.py
    Creating virtualenv in .venv ... [Ok]
    Installing requirements ... [Ok]
    Installing project ... [Ok]
    Creating directories ... [Ok]
    Environment file ... [Ok]

Simple!

You can also compose tasks to decide what to execute and what order.

.. code-block:: python

    #!/usr/bin/env python3
    import os
    import venv

    from boot import step, run, task
    from pathlib import Path

    root_path = Path(__file__).parent.resolve()
    venv_dir = root_path / '.venv'


    @task
    def build(this)
        with step(f'Creating virtualenv in {venv_dir.name}'):
            if not venv_dir.exists():
                venv.create(venv_dir, with_pip=True)

        with step('Creating directories'):
            run(f'mkdir -p public/media')
            run(f'mkdir -p public/static')

        with step('Environment file'):
            envfile = root_path / '.env'

            if not envfile.exists():
                with open(envfile, 'w') as handle:
                    os.chmod(envfile, 0o600)
                    handle.write('')


    @task
    def requirements(this)
        with step('Installing requirements'):
            run(f'{venv_dir / "bin/pip"} install -r requirements.txt')


    @task
    def backup(this)
        with step(f'Backup db'):
            run('pg_dump -d database -f output.sql')


    if __name__ == '__main__':
        tasks = {
            'default': build >> requirements,
            'build': build,
            'requirements': requirements,
        }


        if len(sys.argv) == 1:
            if sys.argv[0] in tasks:
                tasks[sys.argv[0]]()
            else:
                print(f'Unknown task: {sys.argv[0]}')
                print(f'Available tasks are: {tasks.keys()}')
        else:
            default()

