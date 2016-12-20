class Parser(object):

    _NOMORE = ''

    _KWORDS = {
        'and',   'break', 'do',       'else', 'elseif', 'end',
        'false', 'for',   'function', 'goto', 'if',     'in',
        'local', 'nil',   'not',      'or',   'repeat', 'return',
        'then',  'true',  'until',    'while'
    }

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

    def _reset_index(self, index):
        """
        reset the index to an old one
        """
        self._index = index
        self._current = self.source[index]

    def _in_sequence(self, char, sequence):
        """
        check whether a character is in a sequence
        """
        if char != self._NOMORE and char in sequence:
            return True
        else:
            return False

    def _skip_spaces(self):
        """
        skip whitespaces
        """
        while self._current.isspace():
            self._take_next()

    def _skip_newline(self):
        """
        skip newline sequence (\\n, \\r, \\n\\r, or \\r\\n)
        """
        assert self._in_sequence(self._current, '\n\r')
        old = self._current    # skip \n or \r
        self._take_next()
        if self._in_sequence(self._current, '\n\r') and self._current != old:
            self._take_next()  # skip \n\r or \r\n

    def parse_number(self):
        """
        parse a string to a number
        """
        assert self._current.isdigit() or (self._current == '.' and
                                           self._peak_next().isdigit())

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
            elif self._in_sequence(self._current, '\n\r'):
                raise SyntaxError('bad string: unfinished string')
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

        if self._current in escapees:                   # abfnrtv\"'
            char = escapees[self._current]
            self._take_next()
        elif self._in_sequence(self._current, '\n\r'):  # real newline
            char = '\n'
            self._skip_newline()
        elif self._current == 'z':                      # zap following spaces
            char = ''
            self._take_next()
            self._skip_spaces()
        elif self._current.isdigit():                   # \ddd, up to 3 dec
            d_value, d_count = self._parse_digits(10, 3)
            if d_value > 255:
                raise SyntaxError('bad string: decimal value exceeds 255')
            char = chr(d_value)
        elif self._current == 'x':                      # \xXX, exactly 2 hex
            self._take_next()
            x_value, x_count = self._parse_digits(16, 2)
            if x_count != 2:
                raise SyntaxError('bad string: needs exactly 2 hex digits')
            char = chr(x_value)
        else:                                           # whatever
            raise SyntaxError('bad string: invalid escape sequence')

        return char

    def parse_long_string(self, is_comment=False):
        """
        parse a literal long string
        """
        assert self._current == '['
        assert self._in_sequence(self._peak_next(), '=[')

        level, _ = self._parse_long_bracket()
        if level < 0:
            raise SyntaxError('bad long string: invalid long string delimiter')

        if self._in_sequence(self._current, '\n\r'):  # starts with a newline
            self._skip_newline()

        string = ''
        while self._current != self._NOMORE:
            if self._current == ']':
                close_level, _ = self._parse_long_bracket(level, True)
                if close_level < 0:
                    string += ']'
                    self._take_next()
                else:
                    return string
            elif self._in_sequence(self._current, '\n\r'):  # real newline
                string += '\n'
                self._skip_newline()
            else:
                string += self._current
                self._take_next()
        raise SyntaxError('bad long string: unfinished long string')

    def _parse_long_bracket(self, expected_level=None, reset_if_fail=False):
        """
        try to find the level of a long bracket, return negative level if fail
        """
        assert self._in_sequence(self._current, '[]')
        delimiter = self._current
        old_index = self._index

        level = 0
        sequence = delimiter  # consumed character sequence
        self._take_next()
        while self._current == '=':
            level += 1
            sequence += '='
            self._take_next()

        if expected_level is not None and level != expected_level:
            if reset_if_fail:
                self._reset_index(old_index)
            return -1, sequence

        if self._current == delimiter:
            sequence += delimiter
            self._take_next()
            return level, sequence
        else:
            if reset_if_fail:
                self._reset_index(old_index)
            return -1, sequence

    def parse_word(self):
        """
        parse a word (identifier or keyword)
        """
        assert self._current.isalpha() or self._current == '_'

        word = self._current
        self._take_next()
        while self._current.isalnum() or self._current == '_':
            word += self._current
            self._take_next()
        return word


