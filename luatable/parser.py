#!/usr/bin/env python

class Parser(object):

    def __init__(self, source):
        self.source = source
        self.index = 0
        self.current = source[0] if len(source) > 0 else '\0'

    def peak_next(self):
        if self.index + 1 < len(self.source):
            return self.source[self.index + 1]
        else:
            return '\0'

    def take_next(self):
        if self.index + 1 < len(self.source):
            self.index += 1
            self.current = self.source[self.index]
        else:
            self.current = '\0'
        return self.current

    def parse_number(self):
        assert self.current == '.' or self.current.isdigit()

        if self.current == '0' and self.peak_next() in 'xX':
            base = 16
            e_symbols = 'pP'
            e_base = 2
            self.take_next()
            self.take_next()
        else:
            base = 10
            e_symbols = 'eE'
            e_base = 10

        # Integer part
        i_value, i_count = self.parse_integer(base)

        # Fraction part
        f_value, f_count = 0, 0
        if self.current == '.':
            self.take_next()
            f_value, f_count = self.parse_integer(base)
            f_value = f_value / float(base ** f_count)

        # Exponent part
        e_value, e_count = 0, 0
        if self.current in e_symbols:
            self.take_next()
            e_sign = +1
            if self.current in '-+':
                e_sign = -1 if self.current == '-' else +1
                self.take_next()
            e_value, e_count = self.parse_integer(base)
            e_value *= e_sign
            assert e_count > 0

        assert i_count > 0 or f_count > 0
        return (i_value + f_value) * (e_base ** e_value)

    def parse_integer(self, base):
        assert base in (10, 16)
        valid_digits = '0123456789' if base == 10 else '0123456789abcdefABCDEF'

        value, count = 0, 0
        while self.current in valid_digits:
            count += 1
            digit = int(self.current, base=base)
            value = value * base + digit
            self.take_next()
        return value, count

if __name__ == "__main__":
    # Examples from Lua 5.2 Reference Manual
    numbers1 = ['3', '3.0', '3.1416', '314.16e-2', '0.31416E1',
                '0xff', '0x0.1E', '0xA23p-4', '0X1.921FB54442D18P+1']
    # Examples from Programming in Lua 3e
    numbers2 = ['4', '0.4', '4.57e-3', '0.3e12', '5E+20',
                '0xff', '0x1A3', '0x0.2', '0x1p-1', '0xa.bp2']
    for num in numbers1 + numbers2:
        print Parser(num).parse_number()

