# -*- coding: utf-8 -*-
"""
    luatable.generator
    ~~~~~~~~~~~~~~~

    Implements a Lua table generator (encoder)
"""

import string

class Generator(object):
    """
    A generator that is able to generate a Lua table constructor
    or some basic types (nil, boolean, number, and string)
    """

    def __init__(self, obj):
        self._obj = obj

    def generate(self):
        """
        return the Lua representation of the object
        """
        return self._generate(self._obj)

    def _generate(self, obj):
        """
        helper method for self.generate()
        """
        output = ''
        if obj is None:                         # nil
            output += 'nil'
        elif isinstance(obj, bool):             # boolean
            if obj == True:
                output += 'true'
            else:
                output += 'false'
        elif type(obj) in {int, long, float}:   # number
            output += str(obj)
        elif isinstance(obj, str):              # string
            output += '"'
            output += self._generate_string(obj)
            output += '"'
        elif isinstance(obj, list):             # contains list fields only
            output += '{'
            for item in obj:
                output += self._generate(item)
                output += ','
            output += '}'
        elif isinstance(obj, dict):             # contains record fields
            output += '{'
            for key, value in obj.items():
                output += '['
                output += self._generate(key)
                output += ']'
                output += '='
                output += self._generate(value)
                output += ','
            output += '}'
        else:
            raise TypeError('unsupported type: %s' % type(obj))

        return output

    _ESCAPEES = {'\a': 'a', '\b': 'b', '\t': 't', '\n': 'n', '\v': 'v',
                 '\f': 'f', '\r': 'r', '"': '"', "'": "'", '\\': '\\'}

    def _generate_string(self, s):
        """
        generate string contents
        """
        output = ''
        for char in s:
            if char in self._ESCAPEES:
                output += '\\' + self._ESCAPEES[char]
            elif char in string.printable:
                output += char
            else:
                output += '\\x' + format(ord(char), 'x')
        return output

def tolua(obj):
    """
    return a Lua representation of the given object
    """
    generator = Generator(obj)
    return generator.generate()
