pqon
====
pqon is a more consistent version of jq. The full reasoning behind building an alternative to `jq`
can be found an upcoming blog post on my blog <https://blagblogblag.com>.
It takes JSON as input and outputs the transformed JSON.

Install
-------
The recommended way to install `pqon` is via [pipx]:

    pipx pqon

Example usage
-------------
```json5
// example.json
[
  { "name": "Jane Doe", "age": 55 },
  { "name": "John Doe", "age": 41 }
]
```

```bash
> pqon '[].name' example.json
["Jane Doe", "John Doe"]

> jq '.[].name' example.json
"Jane Doe"
"John Doe"
```

```bash
> pqon 'F(.age > 50)' example.json
[{ "name": "Jane Doe", "age": 55 }]

> jq '.[]|select(.age > 50)' example.json
{ "name": "Jane Doe", "age": 55 }
```

```json5
// example-with-children.json
[
  {"name": "Jane Doe", "personal": {"children": [{"name": "Jake", "age": 12}, {"name": "June", "age": 5}]}},
  {"name": "John Doe", "personal": {"children": [{"name": "Justin", "age": 14}, {"name": "John", "age": 11}, {"name": "Jade", "age": 16}]}}
]
```

Sort the `personal.children` sublist but otherwise return all the origin data
```bash
> pqon '???' example-with-children.json
# Perhaps `O(.personal.children, .age)` -- `O` for "order", since "S" is for "select" and thus we can't do `S`/`sort`.
[
  {"name": "Jane Doe", "personal": {"children": [{"name": "June", "age": 5}, {"name": "Jake", "age": 12}]}},
  {"name": "John Doe", "personal": {"children": [{"name": "John", "age": 11}, {"name": "Justin", "age": 14}, {"name": "Jade", "age": 16}]}}
]

> jq '.[].personal.children |= sort_by(.age)' example-with-children.json
[
  {"name": "Jane Doe", "personal": {"children": [{"name": "June", "age": 5}, {"name": "Jake", "age": 12}]}},
  {"name": "John Doe", "personal": {"children": [{"name": "John", "age": 11}, {"name": "Justin", "age": 14}, {"name": "Jade", "age": 16}]}}
]
```
jq's `|=`-operator is quite difficult to wrap your head around here.

One of the things that has been tripping me up is that jq is command-line biased

this means that there are really two internal representations -- one with 
"newline" separated records (for the command line) -- and one that is pure JSON.
Knowing when you're in JSON-land and when you're in command-line land is not
easy to keep track of, and adds to the mental gymnastics required when writing a
script.

* Always-on approach to JSON (internal represenation is JSON-compatible, and output is always JSON)
* Decent error messages

pqon is
-------
* Easier to reason about than `jq` (yes, this is subjective)

pqon is _not_
-------------
* Built for speed (uses the built-in `json`-library in Python)
* Low on memory usage / streaming (parses and stores the full JSON in memory)

Does this return the full `example2.json`, or just the collaborators with an age
above 50?
```bash
> pqon '.collaborators[]F(.age > 50)' example2.json
# Prints only collaborator elements
> pqon 'F(.collaborators.age > 50)' example3.json
# Prints whole top-level object
```

Replace strings
```bash
> pqon '.collaborators[].name|R("Doe", "Johnson")' example2.json
```

```bash
# Get the first country in all countries attributes
> pqon '[].countries[0]'
# Get the value of the "countries"-attribute of the first element in the list
> pqon '([].countries)[0]' == pqon '[0].countries'
```

Alternative tools
-----------------

- [jq](https://stedolan.github.io/jq/) – The "OG"
- [jshon](https://github.com/keenerd/jshon)
- [jtc](https://github.com/ldn-softdev/jtc)
- [fx](https://github.com/antonmedv/fx)
- jp - two tools named "jp": https://github.com/cburgmer/jp and https://github.com/brianm/jp
- [pq](https://github.com/dvolk/pq)
- [zq](https://zed.brimdata.io/docs/commands/zq/) – _I'm not a fan of this one. The "SQL"-like syntax is not an improvement._ ([blog post](https://www.brimdata.io/blog/introducing-zq/) and [Lobste.rs discussion](https://lobste.rs/s/uhkwhn/introducing_zq_easier_faster))
- Plain Python: `echo '[123, { "children": ["a", "b", "c"] }]' | python -c 'import json, sys; print(json.load(sys.stdin)[1]["children"])'`


**Manipulate JSON with Python/Go/...**
- [jello](https://github.com/kellyjonbrazil/jello) – Use Python to manipulate JSON. Input data is set to the `_`-variable.
- [gq](https://github.com/hherman1/gq) – Use Go to manipulate JSON. Input data is set to the `j`-variable. ([Hacker News discussion](https://news.ycombinator.com/item?id=31181898))

**Line-based tools**
- [gron](https://github.com/tomnomnom/gron) (love this idea!)
- JSONL/JSON lines: https://jsonlines.org/

Alternative ideas
-----------------
### Selector / transformer at command line
pqon takes three arguments

```bash
> pqon <selector> <transformers> <file>
```

The selector is which part of the JSON structure you want to have output.
The transformers are any changes you want to make to the JSON structure.

For example:
```bash
people4 = [
    {"name": "Jane Doe", "personal": {"children": [{'name': 'Jake', 'age': 12}]}},
    {"name": "John Doe", "personal": {"children": [{'name': 'Justin', 'age': 14}, {'name': 'John', 'age': 11}, {'name': 'Jade', 'age': 16}]}},
]
> pqon '[].personal.children[].age' '[].personal.children!F(. > 13)' <file>
[[], [14, 16]]
or this other syntax where the transform always works on the output of the selector
> pqon '[].personal.children[].age' 'F(. > 13)' <file>
[[], [14, 16]]
```

### Selector clearly marked in the language
Currently, there are two operators `F` (filter) and `R` (replace) but the selectors are "bare" and not qualified with any name.
We could add a selection operation `S`, and disallow "bare" selection:

```bash
> pqon 'S([].age) | F(. > 50)' example.json
[55]
```

```
> pqon 'F(.age > 50) | S(.personal.children[0])' example-with-children.json
{'name': 'Jake', 'age': 12}
```

### Selector / transformer clearly marked in the language

pqon generally has two kinds of operations:

* Selectors -- always start with a `.`
* Transformers -- always start with a `!`

```bash
people4 = [
    {"name": "Jane Doe", "personal": {"children": [{'name': 'Jake', 'age': 12}]}},
    {"name": "John Doe", "personal": {"children": [{'name': 'Justin', 'age': 14}, {'name': 'John', 'age': 11}, {'name': 'Jade', 'age': 16}]}},
]
> pqon '.[].personal.children.[].age!F(. > 13)' <file>
[[], [14, 16]]
> pqon '.[].personal.children!F(.age > 13)' <file>
[[], [{'name': 'Justin', 'age': 14}, {'name': 'Jade', 'age': 16}]]
# > pqon '!F(.personal.children.[].age > 13)' <file>
> pqon '!F(.personal.children!any(.age > 13))' <file>
[{"name": "John Doe", "personal": {"children": [{'name': 'Justin', 'age': 14}, {'name': 'John', 'age': 11}, {'name': 'Jade', 'age': 16}]}}]
```

Credits
-------
`example4.json` is a hand-written version of [https://en.wikipedia.org/wiki/List_of_physicists]
which is licensed as Creative Commons Attribution-ShareAlike License. Errors may
occur.

Thank you
---------
* https://dev.to/bowmanjd/build-and-test-a-command-line-interface-with-poetry-python-s-argparse-and-pytest-4gab

[pipx]: https://github.com/pypa/pipx
