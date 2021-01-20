import argparse
from functools import partial
import json
import re
import sys

RE_IDENTIFIER = re.compile(r'^[a-z][a-z0-9_]+', re.IGNORECASE)
RE_ARRAY_INDEX = re.compile(r'^\[(\d+)\]')


# fmt: off
parser = argparse.ArgumentParser(description='A JSON-biased alternative to jq')
parser.add_argument('command', help='The jason command to run on the JSON')
parser.add_argument('filename', nargs='?', metavar='files', help='The files to transform')
parser.add_argument('--strict', action='store_true', help='Error on missing attributes')
parser.add_argument('-U', '--unix', action='store_true', help='Output lists with one line per element and quotes removed around strings')
# fmt: on


def attr_access(identifier, strict, obj):
    try:
        return obj[identifier]
    except KeyError:
        if strict:
            raise
        else:
            return None


def entry():
    args = parser.parse_args()
    script = args.command
    filename = args.filename
    strict = args.strict
    unix = args.unix

    if not sys.stdin.isatty():
        current_value = json.load(sys.stdin)
    elif filename:
        with open(filename) as f:
            current_value = json.load(f)

    # Parser
    array_op = False
    while script:
        if script[0:2] == '[]':
            script = script[2:]
            array_op = True
            command = None
        elif script[0:1] == '.':
            script = script[1:]
            identifier = RE_IDENTIFIER.match(script).group(0)
            script = script[len(identifier) :]
            command = partial(attr_access, identifier, strict)
        elif RE_ARRAY_INDEX.match(script):
            match = RE_ARRAY_INDEX.match(script)
            index = int(match.group(1))
            script = script[len(match.group(0)) :]
            command = lambda arr: arr[index]
        else:
            print(f'Unknown command: {script}')
            exit(0)

        if command:
            if array_op:
                current_value = [command(val) for val in current_value]
                array_op = False
            else:
                current_value = command(current_value)

    if type(current_value) is list and unix:
        for el in current_value:
            print(el)
    else:
        print(json.dumps(current_value))


if __name__ == '__main__':
    entry()
