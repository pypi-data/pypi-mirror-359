from hprint import hprint


test_data_1 = [
    {'a': 1, 'b': "1", 'c': 1.0},
    {'a': 2, 'b': "2", 'c': 2.0},
]

test_data_2 = [
    {'a': 1, 'b': "1", 'c': 1.12345},
    {'a': 2, 'b': "2", 'c': 2.12345},
]

test_data_3 = [
    {'a': 1000, 'b': "1000", 'c': 1.2345},
    {'a': 2000000, 'b': "2000", 'c': 1.2345}
]


test_data_4 = [
    {'a': "1e5", 'b': "1000000000"}
]

test_data_5 = [
    {'a': "1", 'b': "2"},
    {'a': "1", 'b': "2", 'c': "3"},
]


def _hprint(*args, **kwargs):
    if "raw" not in kwargs or not kwargs["raw"]:
        kwargs["raw"] = True
    args_str = ", ".join(repr(arg) for arg in args)
    kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
    function_str = f"hprint({args_str}, {kwargs_str})"
    output = hprint(*args, **kwargs)
    print("-> " + function_str)
    print(output)
    output = str(output)
    _output = '\n'.join([line.rstrip() for line in output.splitlines()])
    return _output


def test_missing_value():
    assert _hprint(test_data_5) == """
a    b    c
---  ---  ------
1    2    [none]
1    2    3
"""[1:-1]
    assert _hprint(test_data_5, missing_value='?') == """
a    b    c
---  ---  ---
1    2    ?
1    2    3
"""[1:-1]


def test_header():
    assert _hprint(test_data_5, header=False) == """
-  -  ------
1  2  [none]
1  2  3
-  -  ------
"""[1:-1]


def test_convert():
    assert _hprint(test_data_5, mappings={
        'a': ('a', lambda x: int(x) + 100),
        'c': ('c', 1000, lambda x: int(x) + 200),
    }) == """
a    c
---  ----
101  1200
101  203
"""[1:-1]
    assert _hprint(test_data_5, mappings={
        'a': ('a', lambda x: int(x) + 100),
        'c': ('c', lambda x: int(x) + 100),
    }, convert=False) == """
a    c
---  ------
1    [none]
1    3
"""[1:-1]


def test_numparse():
    assert _hprint(test_data_4, disable_numparse=False) == """
     a           b
------  ----------
100000  1000000000
"""[1:-1]
    assert _hprint(test_data_4) == """
a    b
---  ----------
1e5  1000000000
"""[1:-1]


def test_json_format():
    assert _hprint(test_data_1, json_format=True) == """
[{'a': 1, 'b': '1', 'c': 1.0}, {'a': 2, 'b': '2', 'c': 2.0}]
"""[1:-1]
    assert _hprint(test_data_1, as_json=True) == """
[{'a': 1, 'b': '1', 'c': 1.0}, {'a': 2, 'b': '2', 'c': 2.0}]
"""[1:-1]


def test_offset():
    assert _hprint(test_data_1, x=True) == """
-[ RECORD 1 ]--+----
a              | 1
b              | 1
c              | 1.0
-[ RECORD 2 ]--+----
a              | 2
b              | 2
c              | 2.0
"""[1:-1]
    assert _hprint(test_data_1, x=True, offset=1) == """
-[ RECORD 2 ]--+----
a              | 1
b              | 1
c              | 1.0
-[ RECORD 3 ]--+----
a              | 2
b              | 2
c              | 2.0
"""[1:-1]


def test_numbered():
    assert _hprint(test_data_1, numbered=True) == """
No    a    b    c
----  ---  ---  ---
1     1    1    1.0
2     2    2    2.0
"""[1:-1]


def test_kwargs_floatfmt():
    assert _hprint(test_data_2) == """
a    b    c
---  ---  -------
1    1    1.12345
2    2    2.12345
"""[1:-1]
    assert _hprint(test_data_2, floatfmt='.2f') == """
a    b    c
---  ---  ----
1    1    1.12
2    2    2.12
"""[1:-1]
    assert _hprint(test_data_2, floatfmt='.2f', x=True) == """
-[ RECORD 1 ]--+-----
a              | 1
b              | 1
c              | 1.12
-[ RECORD 2 ]--+-----
a              | 2
b              | 2
c              | 2.12
"""[1:-1]


def test_kwargs_intfmt():
    assert _hprint(test_data_3) == """
a        b     c
-------  ----  ------
1000     1000  1.2345
2000000  2000  1.2345
"""[1:-1]
    assert _hprint(test_data_3, intfmt=",", floatfmt='.2f') == """
a          b     c
---------  ----  ----
1,000      1000  1.23
2,000,000  2000  1.23
"""[1:-1]
    assert _hprint(test_data_3, intfmt=",", floatfmt='.2f', x=True) == """
-[ RECORD 1 ]--+----------
a              | 1,000
b              | 1000
c              | 1.23
-[ RECORD 2 ]--+----------
a              | 2,000,000
b              | 2000
c              | 1.23
"""[1:-1]


def test_kwargs_tablefmt():
    assert _hprint(test_data_1, tablefmt='psql') == """
+-----+-----+-----+
| a   | b   | c   |
|-----+-----+-----|
| 1   | 1   | 1.0 |
| 2   | 2   | 2.0 |
+-----+-----+-----+
"""[1:-1]
    assert _hprint(test_data_1, tablefmt='plain') == """
a    b    c
1    1    1.0
2    2    2.0
"""[1:-1]
