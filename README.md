# LuaTable

LuaTable is a simple parser and generator for Lua tables.

## Examples

```python
>>> from pprint import pprint
>>> from luatable import fromlua, tolua
>>> src = """
...     {
...         list = {
...             3141.6e-3,              -- decimal floating-point expression
...             0xA23p-4;               -- binary floating-point expression
...             '\\97lo\\10\\04923"',               -- single-quoted string
...             "\\x61\\x6c\\x6f\\x0a123\\x22",     -- double-quoted string
...             [==[\nalo\n123"]==]                 -- multi-line string
...         },
...         dict = {
...             [ [[kikyo]]] = true,                -- long string as key
...             ["kagome"] = false,                 -- short string as key
...             inuyasha = nil;                     -- name as key
...             19961113.E-4,               -- positive, empty fraction part
...             -.20080618e4                -- negative, empty integer part
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

## License

LuaTable is MIT licensed.
