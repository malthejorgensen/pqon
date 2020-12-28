jason
=====
For some reason I have never really been able to grok `jq`, whereas grokking
regex was relatively straight-forward.

One of the things that has been tripping me up is that jq is command-line biased

this means that there are really two internal representations -- one with 
"newline" separated records (for the command line) -- and one that is pure JSON.
Knowing when you're in JSON-land and when you're in command-line land is not
easy to keep track of, and adds to the mental gymnastics required when writing a
script.



```json
[
  { "name": 'Jane Doe", "age": 55 },
  { "name": 'John Doe", "age": 41 }
]
```

```bash
> jason '[].name'
["Jane Doe", "John Doe"]

> jq '.[].name'
Jane Doe
John Doe
```

Alternative tools
-----------------

* jq
* jshon
* jtc
* fx
* jp
* jello

Credits
-------
`example4.json` is a hand-written version of [https://en.wikipedia.org/wiki/List_of_physicists]
which is licensed as Creative Commons Attribution-ShareAlike License. Errors may
occur.
