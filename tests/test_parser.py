"""
    tests.test_parser
    ~~~~~~~~~~~~~~~~~

    Lua table parser (decoder)
"""

import unittest

from luatable.parser import Parser

class ParserTestCase(unittest.TestCase):

    def test_parse_number(self):
        # examples from Lua 5.2 Reference Manual
        input1 = ['3', '3.0', '3.1416', '314.16e-2', '0.31416E1',
                  '0xff', '0x0.1E', '0xA23p-4', '0X1.921FB54442D18P+1']
        output1 = [3, 3, 3.1416, 3.1416, 3.1416,
                   255, 0.1171875, 162.1875, 3.1415926535898]
        # examples from Programming in Lua, 3e
        input2 = ['4', '0.4', '4.57e-3', '0.3e12', '5E+20',
                  '0xff', '0x1A3', '0x0.2', '0x1p-1', '0xa.bp2']
        output2 = [4, 0.4, 0.00457, 300000000000, 5e+20,
                   255, 419, 0.125, 0.5, 42.75]

        for i_val, o_val in zip(input1 + input2, output1 + output2):
            self.assertAlmostEqual(Parser(i_val).parse(), o_val)

    def test_parse_string(self):
        # examples from Lua 5.2 Reference Manual
        input1 = ['\'alo\\n123"\'', '"alo\\n123\\""', '\'\\97lo\\10\\04923"\'']
        output1 = 'alo\n123"'
        for i_val in input1:
            self.assertEqual(Parser(i_val).parse(), output1)

        # examples from Programming in Lua, 3e
        input2 = ['"alo\\n123\\""', '\'\\97lo\\10\\04923"\'',
                  "'\\x61\\x6c\\x6f\\x0a\\x31\\x32\\x33\\x22'"]
        output2 = 'alo\n123"'
        for i_val in input2:
            self.assertEqual(Parser(i_val).parse(), output2)

    def test_parse_long_string(self):
        # examples from Lua 5.2 Reference Manual
        input1 = ['[[alo\n123"]]', '[==[\nalo\n123"]==]']
        output1 = 'alo\n123"'
        for i_val in input1:
            self.assertEqual(Parser(i_val).parse(), output1)

        # examples from Programming in Lua, 3e
        page_lines = [
            '[[',
            '<html>',
            '<head>',
            '  <title>An HTML Page</title>',
            '</head>',
            '<body>',
            '  <a href="http://www.lua.org">Lua</a>',
            '</body>',
            '</html>',
            ']]'
        ]
        output2 = '\n'.join(page_lines[1:-1]) + '\n'
        for newline in ('\n', '\r', '\n\r', '\r\n'):
            input2 = newline.join(page_lines)
            self.assertEqual(Parser(input2).parse(), output2)

    def test_parse_table(self):
        # examples from Lua 5.2 Reference Manual
        input1 = '{ ["f(1)"] = "g"; "x", "y"; x = 1, "f(x)", [30] = 23; 45 }'
        output1 = {1: "x", 2: "y", 3: "f(x)", 4: 45,
                   "f(1)": "g", 30: 23, "x": 1}
        self.assertEqual(Parser(input1).parse(), output1)

        # examples from Programming in Lua, 3e
        input2 = """{"Sunday", "Monday", "Tuesday", "Wednesday",
                     "Thursday", "Friday", "Saturday"}"""
        output2 = ['Sunday', 'Monday', 'Tuesday', 'Wednesday',
                   'Thursday', 'Friday', 'Saturday']

        input3 = '{x=10, y=20}'
        output3 = {'y': 20, 'x': 10}

        input4 = '{x=0, y=0, label="console"}'
        output4 = {'label': 'console', 'y': 0, 'x': 0}

        input5 = '{"math.sin(0)", "math.sin(1)", "math.sin(2)"}'
        output5 = ["math.sin(0)", "math.sin(1)", "math.sin(2)"]

        input6 = """{["+"] = "add", ["-"] = "sub",
                     ["*"] = "mul", ["/"] = "div"}"""
        output6 = {'-': "sub", '/': "div", '+': "add", '*': "mul"}

        input7 = '{[20] = "-", [21] = "--", [22] = "---"}'
        output7 = {22: "---", 21: "--", 20: "-"}

        input8 = '{x=10, y=45; "one", "two", "three"}'
        output8 = {1: "one", 2: "two", 3: "three", "y": 45, "x": 10}

        input9 = '{[1]="red", [2]="green", [3]="blue",}'
        output9 = {1: "red", 2: "green", 3: "blue"}

        inputs = [input2, input3, input4, input5,
                  input6, input7, input8, input9]
        outputs = [output2, output3, output4, output5,
                   output6, output7, output8, output9]
        for i_val, o_val in zip(inputs, outputs):
            self.assertEqual(Parser(i_val).parse(), o_val)

    def test_parse_value(self):
        # examples from Programming in Lua, 3e
        input1 = """
            {color="blue",
             thickness=2,
             npoints=4,
             {x=0,   y=0},  -- polyline[1]
             {x=-10, y=0},  -- polyline[2]
             {x=-10, y=1},  -- polyline[3]
             {x=0,   y=1}   -- polyline[4]
            }
        """
        output1 = {
            1: {'y': 0,'x':   0},
            2: {'y': 0,'x': -10},
            3: {'y': 1,'x': -10},
            4: {'y': 1,'x':   0},
            'thickness': 2,
            'npoints': 4,
            'color': "blue"
        }
        self.assertEqual(Parser(input1).parse(), output1)
