import argparse
import sys
from collections import OrderedDict


class ActionsCommand:
    def __init__(self, **actions):
        self._actions = OrderedDict()

        for name, action in actions.items():
            if not callable(action):
                raise TypeError('action is not callable')

            self._actions[name] = action

        self.parser = argparse.ArgumentParser()

        self.parser.add_argument(
            '-l', '--list', action='store_true', default=False,
            help='List all available actions')

        self.parser.add_argument(
            'action',
            help='Action to perform. multiple mentions allowed',
            metavar='action', nargs='*')

    def run(self, args: list = None):
        if not args:
            args = sys.argv

        has_default = 'default' in self._actions

        if not args[1:] and has_default:
            self._actions['default']()
        else:
            options = self.parser.parse_args(args[1:])

            if options.list:
                for name, action in self._actions.items():
                    description = getattr(action, '__doc__', None)

                    if description:
                        print(f'{name:<20}{description}')
                    else:
                        print(name)
            else:
                for name in options.action:
                    if name not in self._actions:
                        print(f'Unkwnon action: {name}')
                        return

                for name in options.action:
                    self._actions[name]()

    @classmethod
    def main(cls, **kwargs):
        cli = cls(**kwargs)
        cli.run()
