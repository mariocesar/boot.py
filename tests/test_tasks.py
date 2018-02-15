from collections import Callable

from boot.api import task, Task


def test_task_constructor():
    @task
    def task_foo(this):
        pass

    assert isinstance(task_foo, Task)
    assert isinstance(task_foo, Callable)


def test_task_call():
    @task
    def task_foo(this):
        this['foo'] = 1

    @task
    def task_bar(this):
        return "Hello"

    assert task_foo()['foo'] == 1
    assert dict(task_bar()) == {}


def test_task_composition():
    @task
    def task_foo(this):
        this['foo'] = 1

    @task
    def task_bar(this):
        this['bar'] = 2

    new_task = task_foo >> task_bar

    assert len(new_task._queue) == 2
    assert isinstance(new_task, Task)

    assert dict(new_task()) == {'bar': 2, 'foo': 1}
    assert dict(new_task()) == {'bar': 2, 'foo': 1}

    @task
    def task_again(this):
        this['again'] = 3

    new_task >>= task_again

    assert dict(new_task()) == {'bar': 2, 'foo': 1, 'again': 3}

    new_task = new_task >> new_task

    assert len(new_task._queue) == 6