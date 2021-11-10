from jason.parser import gobble_backslashed_str, parse_selector, parse_literal, parser


def test_gobble_backslashed_str():
    assert gobble_backslashed_str('abc"') == ('abc', 3)
    assert gobble_backslashed_str(r'abc\"def"') == ('abc"def', 8)
    assert gobble_backslashed_str(r'abc\\"def"') == ('abc\\', 5)
    assert gobble_backslashed_str(r'abc\\\"def"') == ('abc\\"def', 10)
    assert gobble_backslashed_str(r'abc\def"') == ('abcdef', 7)


def test_parse_selector():
    getter, idx = parse_selector('["abc"] < 50', strict=True)
    assert idx == 7
    assert getter({'abc': 123}) == 123

    getter, idx = parse_selector('["abc"]["def"] < 50', strict=True)
    assert idx == 14
    assert getter({'abc': {'def': 456}}) == 456

    getter, idx = parse_selector('["1 2 3"].def["æøå"][3] < 50', strict=True)
    assert idx == 23
    assert getter({'1 2 3': {'def': {'æøå': [7, 8, 9, 10]}}}) == 10

    getter, idx = parse_selector('["1 2 3"][2].def["æøå"] < 50', strict=True)
    assert idx == 23
    assert getter({'1 2 3': [4, 5, {'def': {'æøå': 789}}]}) == 789


def test_parse_array_selector():
    getter, idx = parse_selector('[2]', strict=True)
    assert idx == 3
    assert getter([1, 2, 3, 4, 5]) == 3

    getter, idx = parse_selector('[:3]', strict=True)
    assert idx == 4
    assert getter([1, 2, 3, 4, 5]) == [1, 2, 3]

    getter, idx = parse_selector('[1:3]', strict=True)
    assert idx == 5
    assert getter([1, 2, 3, 4, 5]) == [2, 3]

    getter, idx = parse_selector('[3:]', strict=True)
    assert idx == 4
    assert getter([1, 2, 3, 4, 5]) == [4, 5]


def test_parse_literal():
    assert parse_literal('123]') == (123, 3)
    assert parse_literal('"goose duck"]') == ('goose duck', 12)


people = [{"name": "Jane Doe", "age": 55}, {"name": "John Doe", "age": 41}]
people2 = [
    {"name": "Jane Doe", "personal": {"number of children": 1}},
    {"name": "John Doe", "personal": {"number of children": 3}},
]
people3 = [
    {"name": "Jane Doe", "personal": {"children": ['Jake']}},
    {"name": "John Doe", "personal": {"children": ['Justin', 'John', 'Jade']}},
]
people4 = [
    {"name": "Jane Doe", "personal": {"children": [{'name': 'Jake', 'age': 12}]}},
    {
        "name": "John Doe",
        "personal": {
            "children": [
                {'name': 'Justin', 'age': 14},
                {'name': 'John', 'age': 11},
                {'name': 'Jade', 'age': 16},
            ]
        },
    },
]


def test_parser():
    assert parser('F(.age > 50)', people) == [people[0]]
    assert parser('F(.age == 41)', people) == [people[1]]
    assert parser('F(.personal["number of children"] <= 2)', people2) == [people2[0]]
    assert parser('[].personal.children', people3) == [
        ['Jake'],
        ['Justin', 'John', 'Jade'],
    ]
    assert parser('[].personal.children[].age', people4) == [
        [12],
        [14, 11, 16],
    ]
    assert parser('[].personal.children|F(.age > 13)|[].name', people4) == [
        [],
        ['Justin', 'Jade'],
    ]
