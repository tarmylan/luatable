"""
    luatable.generator
    ~~~~~~~~~~~~~~~~~~

    Implements a Lua table generator (encoder)
"""

import string

class Generator:

    def __init__(self, obj):
        self._obj = obj

    def generate(self):
        """
        return the Lua representation of the object
        """
        return self._generate(self._obj)

    def _generate(self, obj):
        """
        the workhorse
        """
        output = ''
        if obj is None:                         # nil
            output += 'nil'
        elif isinstance(obj, bool):             # boolean
            if obj == True:
                output += 'true'
            else:
                output += 'false'
        elif isinstance(obj, (int, float)):     # number
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
                if not isinstance(key, (int, float, str)):
                    message = "unsupported key type '%s'" % type(key)
                    raise TypeError(message)
                output += '['
                output += self._generate(key)
                output += ']'
                output += '='
                output += self._generate(value)
                output += ','
            output += '}'
        else:                                   # whatever
            raise TypeError("unsupported object type '%s'" % type(obj))
        return output

    _ESCAPEES = {'\a': 'a', '\b': 'b', '\t': 't', '\n': 'n', '\v': 'v',
                 '\f': 'f', '\r': 'r',  '"': '"',  "'": "'", '\\': '\\'}

    _PRINTABLE = set(string.printable)

    def _generate_string(self, s):
        """
        generate string contents
        """
        output = ''
        for char in s:
            if char in self._ESCAPEES:
                output += '\\' + self._ESCAPEES[char]
            elif char in self._PRINTABLE:
                output += char
            else:
                output += '\\x' + format(ord(char), 'x')
        return output

def tolua(obj):
    """
    return the Lua representation of the given object
    """
    generator = Generator(obj)
    return generator.generate()
