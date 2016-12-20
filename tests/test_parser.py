import unittest
from luatable.parser import Parser

class ParserTestCase(unittest.TestCase):

    def test_parse_number(self):
        # Examples from Lua 5.2 Reference Manual
        input1 = ['3', '3.0', '3.1416', '314.16e-2', '0.31416E1',
                  '0xff', '0x0.1E', '0xA23p-4', '0X1.921FB54442D18P+1']
        output1 = [3, 3, 3.1416, 3.1416, 3.1416,
                   255, 0.1171875, 162.1875, 3.1415926535898]
        # Examples from Programming in Lua, 3e
        input2 = ['4', '0.4', '4.57e-3', '0.3e12', '5E+20',
                  '0xff', '0x1A3', '0x0.2', '0x1p-1', '0xa.bp2']
        output2 = [4, 0.4, 0.00457, 300000000000, 5e+20,
                   255, 419, 0.125, 0.5, 42.75]

        for i_val, o_val in zip(input1 + input2, output1 + output2):
            self.assertAlmostEqual(Parser(i_val).parse_number(), o_val)

    def test_parse_string(self):
        # Examples from Lua 5.2 Reference Manual
        input1 = ['\'alo\\n123"\'', '"alo\\n123\\""', '\'\\97lo\\10\\04923"\'']
                 # '[[alo\n123"]]', '[==[\nalo\n123"]==]']
        output1 = 'alo\n123"'
        for i_val in input1:
            self.assertEqual(Parser(i_val).parse_string(), output1)

        # Examples from Programming in Lua, 3e
        input2 = ['"alo\\n123\\""', '\'\\97lo\\10\\04923"\'',
                  "'\\x61\\x6c\\x6f\\x0a\\x31\\x32\\x33\\x22'"]
        output2 = 'alo\n123"'
        for i_val in input2:
            self.assertEqual(Parser(i_val).parse_string(), output2)
