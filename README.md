pqon
=====
pqon is a more consistent version of jq. The full reasoning behind building an alternative to `jq`
can be found in this blog post ([https://malthejorgensen.com/blog/<slug>]).
It takes JSON as input and outputs that JSON.

Examples
--------
```json
# example.json
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
> pqon 'F(.age > 50).name' example.json
[{ "name": "Jane Doe", "age": 55 }]

> jq '.[]|select(.age > 50)' example.json
{ "name": "Jane Doe", "age": 55 }
```

One of the things that has been tripping me up is that jq is command-line biased

this means that there are really two internal representations -- one with 
"newline" separated records (for the command line) -- and one that is pure JSON.
Knowing when you're in JSON-land and when you're in command-line land is not
easy to keep track of, and adds to the mental gymnastics required when writing a
script.

* Always-on approach to JSON (internal represenation is JSON-compatible, and output is always JSON)
* Decent error messages

pqon is
--------
* Easier to reason about than `jq` (yes, this is subjective)

pqon is _not_
--------------
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

* jq
* [jshon](https://github.com/keenerd/jshon)
* [jtc](https://github.com/ldn-softdev/jtc)
* [fx](https://github.com/antonmedv/fx)
* [jp]()
* [jello](https://github.com/kellyjonbrazil/jello)

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
