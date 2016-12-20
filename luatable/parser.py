class Parser(object):

    _NOMORE = ''

    def __init__(self, source):
        self._source = source
        self._index = 0
        self._current = source[0] if len(source) > 0 else self._NOMORE

    def _peak_next(self):
        """
        return the next character, leave the index unchanged
        """
        if self._index + 1 < len(self._source):
            return self._source[self._index + 1]
        else:
            return self._NOMORE

    def _take_next(self):
        """
        return the next character, advance the index
        """
        if self._index + 1 < len(self._source):
            self._index += 1
            self._current = self._source[self._index]
        else:
            self._index = len(self._source)
            self._current = self._NOMORE
        return self._current

    def _in_sequence(self, char, sequence):
        """
        check whether a character is in a sequence
        """
        if char != self._NOMORE and char in sequence:
            return True
        else:
            return False

    def parse_number(self):
        """
        parse a string to a number
        """
        assert self._current == '.' or self._current.isdigit()

        if self._current == '0' and self._in_sequence(self._peak_next(), 'xX'):
            base = 16
            e_symbols = 'pP'
            e_base = 2
            self._take_next()  # for '0'
            self._take_next()  # for 'x' or 'X'
        else:
            base = 10
            e_symbols = 'eE'
            e_base = 10

        # integer part
        i_value, i_count = self._parse_digits(base)

        # fraction part
        f_value, f_count = 0, 0
        if self._current == '.':
            self._take_next()
            f_value, f_count = self._parse_digits(base)
            f_value = f_value / float(base ** f_count)

        # exponent part
        e_value, e_count = 0, 0
        if self._in_sequence(self._current, e_symbols):
            self._take_next()
            e_sign = +1
            if self._in_sequence(self._current, '-+'):
                e_sign = -1 if self._current == '-' else +1
                self._take_next()
            e_value, e_count = self._parse_digits(base)
            e_value *= e_sign
            if e_count == 0:
                raise SyntaxError('bad number: empty exponent part')

        if i_count == 0 and f_count == 0:
            raise SyntaxError('bad number: empty integer and fraction part')
        return (i_value + f_value) * (e_base ** e_value)

    def _parse_digits(self, base, limit=None):
        """
        parse a sequence of digits to an integer
        """
        valid_digits = '0123456789' if base == 10 else '0123456789abcdefABCDEF'

        value, count = 0, 0
        while self._in_sequence(self._current, valid_digits):
            count += 1
            digit = int(self._current, base=base)
            value = value * base + digit
            self._take_next()
            if limit is not None and count >= limit:
                break
        return value, count

    def parse_string(self):
        """
        parse a literal short string
        """
        assert self._in_sequence(self._current, ['"', "'"])

        delimiter = self._current
        self._take_next()

        string = ''
        while self._current != self._NOMORE:
            if self._current == delimiter:
                self._take_next()
                return string
            elif self._current == '\\':
                self._take_next()
                string += self._parse_escapee()
            else:
                string += self._current
                self._take_next()
        raise SyntaxError('bad string: unfinished string')

    def _parse_escapee(self):
        """
        parse an escape sequence
        """
        escapees = {'a': '\a', 'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r',
                    't': '\t', 'v': '\v', '"': '"', "'": "'", '\\': '\\'}

        if self._current in escapees:           # abfnrtv\"'
            char = escapees[self._current]
            self._take_next()
        elif self._current == '\n':             # real newline
            char = '\n'
            self._take_next()
        elif self._current == 'z':              # skips whitespaces
            char = ''
            self._take_next()
            while self._current.isspace():
                self._take_next()
        elif self._current.isdigit():           # \ddd, up to 3 dec digits
            d_value, d_count = self._parse_digits(10, 3)
            if d_value > 255:
                raise SyntaxError('bad string: numerical value exceeds 255')
            char = chr(d_value)
        elif self._current == 'x':              # \xXX, exactly 2 hex digits
            self._take_next()
            x_value, x_count = self._parse_digits(16, 2)
            if x_count != 2:
                raise SyntaxError('bad string: needs exactly 2 hex digits')
            char = chr(x_value)
        else:                                   # whatever
            raise SyntaxError('bad string: unexpected escape sequence')

        return char

