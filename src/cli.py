import argparse
from functools import partial
import json
import re

RE_IDENTIFIER = re.compile(r'^[a-z][a-z0-9_]+', re.IGNORECASE)
RE_ARRAY_INDEX = re.compile(r'^\[(\d+)\]')


parser = argparse.ArgumentParser(description='A JSON-biased alternative to jq')
parser.add_argument('command', help='The jason command to run on the JSON')
parser.add_argument('filename', metavar='files', help='The files to transform')

def attr_access(identifier, obj):
    return obj[identifier]

def entry():
    args = parser.parse_args()
    script = args.command
    filename = args.filename

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
            script = script[len(identifier):]
            command = partial(attr_access, identifier)
        elif RE_ARRAY_INDEX.match(script):
            match = RE_ARRAY_INDEX.match(script)
            index = int(match.group(1))
            script = script[len(match.group(0)):]
            command = lambda arr: arr[index]

        if command:
            if array_op:
                current_value = [command(val) for val in current_value]
                array_op = False
            else:
                current_value = command(current_value)

    print(json.dumps(current_value))


if __name__ == '__main__':
    entry()
