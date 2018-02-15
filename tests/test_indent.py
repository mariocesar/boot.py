from boot import indent, echo


def test_step_stdout(capsys):
    with indent():
        echo('hello')
        echo('world')

    captured = capsys.readouterr()
    assert captured.out == '    hello\n    world\n'



def test_step_multiple_indents(capsys):

    echo('')
    echo('1')

    with indent():
        echo('1.1')

        with indent():
            echo('1.1.1')

            with indent():
                echo('1.1.1.1')
                echo('1.1.1.2')

    echo('2')

    captured = capsys.readouterr()
    out = captured.out

    assert out == """
1
    1.1
        1.1.1
            1.1.1.1
            1.1.1.2
2
"""