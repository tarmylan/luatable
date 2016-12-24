# -*- coding: utf-8 -*-
"""
    tests.test_generator
    ~~~~~~~~~~~~~~~~~~~~

    Lua table generator (encoder)
"""

import unittest

from luatable.generator import Generator
from luatable.parser import Parser

class GeneratorTestCase(unittest.TestCase):

    def test_generate(self):
        # examples from Programming in Lua, 3e
        input1 = {
            1: {'y': 0, 'x':   0},
            2: {'y': 0, 'x': -10},
            3: {'y': 1, 'x': -10},
            4: {'y': 1, 'x':   0},
            'thickness': 2,
            'npoints': 4,
            'color': "blue"
        }
        generated1 = Generator(input1).generate()
        output1 = Parser(generated1).parse()
        self.assertEqual(input1, output1)
