import argparse
from functools import partial
import json
import re
import sys

from .parser import parser

RE_IDENTIFIER = re.compile(r'^[a-z][a-z0-9_]+', re.IGNORECASE)
RE_ARRAY_INDEX = re.compile(r'^\[(\d+)\]')


# fmt: off
argparser = argparse.ArgumentParser(description='A JSON-biased alternative to jq')
argparser.add_argument('command', help='The pqon command to run on the JSON')
argparser.add_argument('filename', nargs='?', metavar='files', help='The files to transform')
argparser.add_argument('--strict', action='store_true', help='Error on missing attributes')
argparser.add_argument('-U', '--unix', action='store_true', help='Output lists with one line per element and quotes removed around strings')
argparser.add_argument('-N', '--allow-nulls', action='store_true', help='Allow nulls in output')
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
    args = argparser.parse_args()
    script = args.command
    filename = args.filename
    strict = args.strict
    allow_nulls = args.allow_nulls
    unix = args.unix

    if not sys.stdin.isatty():
        current_value = json.load(sys.stdin)
    elif filename:
        with open(filename) as f:
            current_value = json.load(f)

    current_value = parser(script, current_value, strict, allow_nulls)

    if type(current_value) is list and unix:
        for el in current_value:
            print(el)
    else:
        print(json.dumps(current_value, indent=2))


if __name__ == '__main__':
    entry()
