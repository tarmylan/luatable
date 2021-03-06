"""
    tests.test_module
    ~~~~~~~~~~~~~~~~~

    The luatable module
"""

import unittest

from luatable import fromlua, tolua

class ModuleTestCase(unittest.TestCase):

    def test_fromlua_and_tolua(self):
        input1 = """
            {
                list = {
                    3141.6e-3,                  -- decimal floating-point number
                    0xA23p-4;                   -- binary floating-point number
                    '\\97lo\\10\\04923"',               -- single-quoted string
                    "\\x61\\x6c\\x6f\\x0a123\\x22",     -- double-quoted string
                    [==[\nalo\n123"]==],                -- multi-line string
                },
                dict = {
                    [ [[kikyo]]] = true,                -- long string as key
                    ["kagome"] = false,                 -- short string as key
                    inuyasha = nil;                     --[[ name as key
                                                             will be ignored ]]
                    19961113.E-4,               -- positive, empty fraction part
                    -.20080618e4,               -- negative, empty integer part
                }
            }
        """
        output1 = {
            "list": [
                3.1416,
                162.1875,
                "alo\n123\"",
                "alo\n123\"",
                "alo\n123\""
            ],
            "dict": {
                1: 1996.1113,
                2: -2008.0618,
                "kikyo": True,
                "kagome": False
            }
        }

        self.assertEqual(fromlua(input1), output1)
        self.assertEqual(fromlua(tolua(fromlua(input1))), output1)
