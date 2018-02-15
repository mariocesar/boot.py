from boot import step
from boot.types import Color


def test_step_stdout(capsys):
    with step('Step description'):
        pass

    captured = capsys.readouterr()

    assert captured.out == f'Step description ... {Color.bold_green}[Ok]{Color.reset}\n'


def test_step_failed(capsys):
    with step('Failing step'):
        raise Exception()

    captured = capsys.readouterr()
    assert captured.out == f'Failing step ... {Color.bold_red}[Error]{Color.reset}\n' \
                           f'Exception()\n'
