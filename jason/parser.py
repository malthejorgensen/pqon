import argparse
from functools import partial
import json
import re
import sys

RE_IDENTIFIER = re.compile(r'^[a-z][a-z0-9_]+', re.IGNORECASE)
RE_ARRAY_INDEX = re.compile(r'^\[((\d+:\d+)|(\d+:)|(:\d+)|(\d+))\]')


def attr_access(identifier, strict, obj):
    try:
        return obj[identifier]
    except KeyError:
        if strict:
            raise
        else:
            return None


# def parse_error(state, msg):
def parse_error(msg):
    # print(msg)
    raise ValueError(msg)
    spaces = state['column'] * ' '
    print(
        f'''
    {msg}

    {script}
    {spaces}^
'''
    )


def gobble_backslashed_str(b_str):
    idx = 0
    identifier = ''
    backslash_state = 0

    while idx < len(b_str):
        if b_str[idx] == '"' and backslash_state == 0:
            # End of string
            return identifier, idx
        elif b_str[idx] == '"' and backslash_state == 1:
            # Backslashed quote
            identifier += '"'
            backslash_state = 0
        elif b_str[idx] == '\\' and backslash_state == 0:
            # Start of backslashed character
            backslash_state = 1
        elif b_str[idx] == '\\' and backslash_state == 1:
            # Backslashed backslash
            identifier += '\\'
            backslash_state = 0
        else:
            identifier += b_str[idx]
            backslash_state = 0

        idx += 1

    parse_error('Expected end of quoted string')


def parse_selector(selector, strict):
    if selector == '':
        return (lambda x: x, 0)
    elif selector[0:2] == '[]':
        return (lambda x: x, 0)
    elif selector[0] == '[':
        if selector[1] == '"':
            # gobble up until "
            identifier, idx = gobble_backslashed_str(selector[2:])
            # Step over `["` and `"`
            idx += 3

            getter = partial(attr_access, identifier, strict)
        elif re.match(r'\d|:', selector[1]):
            # gobble up until ]

            idx = None
            match = re.match(r'(\d+):(\d+)', selector[1:])
            if match:
                idx = 1 + len(match.group(0))
                begin = int(match.group(1))
                end = int(match.group(2))
                getter = lambda arr: arr[begin:end]
            match = re.match(r':(\d+)', selector[1:])
            if idx is None and match:
                idx = 1 + len(match.group(0))
                until = int(match.group(1))
                getter = lambda arr: arr[:until]
            match = re.match(r'(\d+):', selector[1:])
            if idx is None and match:
                idx = 1 + len(match.group(0))
                begin = int(match.group(1))
                getter = lambda arr: arr[begin:]
            match = re.match(r'(\d+)', selector[1:])
            if idx is None:
                idx = 1 + len(match.group(0))
                arr_index = int(match.group(1))
                getter = lambda arr: arr[arr_index]

        else:
            parse_error('Expected selector: `"` or digit')

        if selector[idx] != ']':
            parse_error(f'Expected end of selector: `]` instead of `{selector[idx]}`')

        # Step over `]`
        idx += 1
    elif selector[0] == '.':
        identifier = RE_IDENTIFIER.match(selector[1:]).group(0)
        idx = 1 + len(identifier)
        getter = partial(attr_access, identifier, strict)
    else:
        return (lambda x: x, 0)

    next_getter, next_idx = parse_selector(selector[idx:], strict)

    return (lambda x: next_getter(getter(x)), idx + next_idx)


def parse_operator(operator):
    if operator[0:2] == '==':
        return (lambda x, y: x == y, 2)
    elif operator[0:2] == '>=':
        return (lambda x, y: x >= y, 2)
    elif operator[0:2] == '<=':
        return (lambda x, y: x <= y, 2)
    elif operator[0] == '>':
        return (lambda x, y: x > y, 1)
    elif operator[0] == '<':
        return (lambda x, y: x < y, 1)
    else:
        parse_error(
            f'Expected comparison operator (==, >=, <=, <, >) not `{operator[0:2]}`'
        )


def parse_literal(literal):
    if re.match(r'\d', literal[0]):
        # gobble up until
        match = re.match(r'\d+', literal)
        number = int(match.group(0))
        idx = len(match.group(0))
        return number, idx
    elif literal[0] == '"':
        literal_str, idx = gobble_backslashed_str(literal[1:])
        # Skip over starting and ending `"`
        return literal_str, idx + 2
    else:
        parse_error(f'Expected literal (string or number) not `{literal[0:5]}...`')


def parser(script, current_value, strict=True, allow_nulls=False):
    # Parser
    array_op = False
    while script:
        if script[0] == '|':
            script = script[1:]
            command = None
        elif script[0] == 'F':
            if script[1] != '(':
                parse_error('Saw F-expression and expected "("')

            getter, idx1 = parse_selector(script[2:], strict)
            idx = 3 + idx1

            operator, idx2 = parse_operator(script[idx:])
            idx += idx2 + 1

            literal, idx3 = parse_literal(script[idx:])
            idx += idx3

            if script[idx] != ')':
                parse_error('Expected F-expression to end with ")"')
            idx += 1

            command = lambda l: [el for el in l if operator(getter(el), literal)]
            script = script[idx:]
        elif script[0:2] == '[]':
            script = script[2:]
            array_op = True
            command = None
        elif script[0:1] == '.':
            getter, idx = parse_selector(script[0:], strict)
            command = getter
            script = script[idx:]
        elif RE_ARRAY_INDEX.match(script):
            getter, idx = parse_selector(script[0:], strict)
            command = getter
            script = script[idx:]
        else:
            print(f'Unknown command: {script}')
            exit(0)

        if array_op:
            current_value = [
                parser(script, val, strict, allow_nulls) for val in current_value
            ]
            if not allow_nulls:
                current_value = [val for val in current_value if val is not None]
            break
        elif command:
            current_value = command(current_value)

    return current_value
