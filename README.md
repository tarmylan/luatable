# LuaTable

This is a simple implementation of Lua table parser and generator for Python 2.7 and Python 3.5. It is pure Python code with no dependencies.

## Usage

Basic parsing:

```python
>>> from luatable import fromlua
>>> src = '{"foo", {["bar"] = {"baz", nil, 1.0, 2}}}'
>>> fromlua(src)
['foo', {'bar': ['baz', None, 1.0, 2]}]
```

Basic generating:

```python
>>> from luatable import tolua
>>> obj = ['foo', {'bar': ['baz', None, 1.0, 2]}]
>>> tolua(obj)
'{"foo",{["bar"]={"baz",nil,1.0,2,},},}'
```

Put it together:

```python
>>> from pprint import pprint
>>> from luatable import fromlua, tolua
>>> src = """
...     {
...         list = {
...             3141.6e-3,                  -- decimal floating-point number
...             0xA23p-4;                   -- binary floating-point number
...             '\\97lo\\10\\04923"',               -- single-quoted string
...             "\\x61\\x6c\\x6f\\x0a123\\x22",     -- double-quoted string
...             [==[\nalo\n123"]==],                -- multi-line string
...         },
...         dict = {
...             [ [[kikyo]]] = true,                -- long string as key
...             ["kagome"] = false,                 -- short string as key
...             inuyasha = nil;                     --[[ name as key
...                                                      will be ignored ]]
...             19961113.E-4,               -- positive, empty fraction part
...             -.20080618e4,               -- negative, empty integer part
...         }
...     }
... """
>>> pprint(fromlua(src))
{'dict': {1: 1996.1113, 2: -2008.0618, 'kagome': False, 'kikyo': True},
 'list': [3.1416, 162.1875, 'alo\n123"', 'alo\n123"', 'alo\n123"']}
>>> pprint(tolua(fromlua(src)))
'{["list"]={3.1416,162.1875,"alo\\n123\\"","alo\\n123\\"","alo\\n123\\"",},["dict"]={[1]=1996.1113,["kikyo"]=true,["kagome"]=false,[2]=-2008.0618,},}'
>>> pprint(fromlua(tolua(fromlua(src))))
{'dict': {1: 1996.1113, 2: -2008.0618, 'kagome': False, 'kikyo': True},
 'list': [3.1416, 162.1875, 'alo\n123"', 'alo\n123"', 'alo\n123"']}
>>> assert fromlua(src) == fromlua(tolua(fromlua(src)))
>>>
```

## Implementation Details

The parser performs the following translations.

| Lua                | Python  |
| ------------------ | ------- |
| `table` (w/ keys)  | `dict`  |
| `table` (w/o keys) | `list`  |
| `string`           | `str`   |
| `number` (int)     | `int`   |
| `number` (real)    | `float` |
| `true`             | `True`  |
| `false`            | `False` |
| `nil`              | `None`  |

The generator performs the following translations.

| Python  | Lua                    |
| ------- | ---------------------- |
| `dict`  | `table` (record style) |
| `list`  | `table` (array style)  |
| `str`   | `string`               |
| `int`   | `number`               |
| `float` | `number`               |
| `True`  | `true`                 |
| `False` | `false`                |
| `None`  | `nil`                  |
