# -*- coding: utf-8 -*-
"""
    luatable.parser
    ~~~~~~~~~~~~~~~

    Implements a recursive descent Lua table parser (decoder)
"""

class Parser(object):
    """
    A parser that is able to decode table constructor
    or some basic types (nil, boolean, number, and string)
    """

    # empty string as end of source indicator
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

    def _reset_index(self, index):
        """
        reset the index to an old one
        """
        self._index = index
        self._current = self._source[index]

    def _in_sequence(self, char, sequence):
        """
        check whether a character is in a sequence
        """
        if char != self._NOMORE and char in sequence:
            return True
        else:
            return False

    def _skip_comment(self):
        """
        skip a short/long comment
        """
        assert self._comment_coming()
        self._take_next()  # for the 1st '-'
        self._take_next()  # for the 2nd '-'

        if self._current == '[':
            level = self._parse_long_bracket(reset_if_fail=True,
                                             reset_if_succeed=True)
            if level >= 0:  # long comment
                try:
                    self.parse_long_string()
                except SyntaxError as e:
                    raise SyntaxError('bad long comment')
                return

        # short comment
        while self._current != self._NOMORE:
            if self._in_sequence(self._current, '\n\r'):
                self._skip_newline()
                break
            else:
                self._take_next()

    def _skip_spaces(self):
        """
        skip whitespaces and comments
        """
        while True:
            converged = True
            while self._current.isspace():
                converged = False
                self._take_next()
            if self._comment_coming():
                converged = False
                self._skip_comment()
            if converged:
                break

    def _skip_newline(self):
        """
        skip newline sequence (\\n, \\r, \\n\\r, or \\r\\n)
        """
        assert self._in_sequence(self._current, '\n\r')
        old = self._current
        self._take_next()      # skip \n or \r
        if self._in_sequence(self._current, '\n\r') and self._current != old:
            self._take_next()  # skip \n\r or \r\n

    def _number_coming(self):
        """
        check whether a number is coming
        """
        return self._current.isdigit() or (self._current == '.' and
                                           self._peak_next().isdigit())

    def _string_coming(self):
        """
        check whether a short string is coming
        """
        return self._in_sequence(self._current, ['"', "'"])

    def _long_string_coming(self):
        """
        check whether a long string is coming
        """
        return (self._current == '[' and
                self._in_sequence(self._peak_next(), '=['))

    def _word_coming(self):
        """
        check whether a word is coming
        """
        return self._current.isalpha() or self._current == '_'

    def _table_coming(self):
        """
        check whether a table is coming
        """
        return self._current == '{'

    def _comment_coming(self):
        """
        check whether a comment is coming
        """
        return self._current == '-' and self._peak_next() == '-'

    def parse_number(self):
        """
        parse a string to a number
        """
        assert self._number_coming()

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
        valid_digits = '0123456789abcdefABCDEF' if base == 16 else '0123456789'

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
        assert self._string_coming()

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

    _ESCAPEES = {'a': '\a', 'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r',
                 't': '\t', 'v': '\v', '"': '"', "'": "'", '\\': '\\'}

    def _parse_escapee(self):
        """
        parse an escape sequence
        """
        if self._current in self._ESCAPEES:             # abfnrtv\"'
            char = self._ESCAPEES[self._current]
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
                raise SyntaxError('bad string: esc: decimal value exceeds 255')
            char = chr(d_value)
        elif self._current == 'x':                      # \xXX, exactly 2 hex
            self._take_next()
            x_value, x_count = self._parse_digits(16, 2)
            if x_count != 2:
                raise SyntaxError('bad string: esc: need exactly 2 hex digits')
            char = chr(x_value)
        else:                                           # whatever
            raise SyntaxError('bad string: esc: invalid escape sequence')

        return char

    def parse_long_string(self, is_comment=False):
        """
        parse a literal long string
        """
        assert self._long_string_coming()

        level = self._parse_long_bracket()
        if level < 0:
            raise SyntaxError('bad long string: invalid long string delimiter')

        if self._in_sequence(self._current, '\n\r'):  # starts with a newline
            self._skip_newline()

        string = ''
        while self._current != self._NOMORE:
            if self._current == ']':
                close_level = self._parse_long_bracket(level,
                                                       reset_if_fail=True)
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

    def _parse_long_bracket(self, expected_level=None,
                            reset_if_fail=False, reset_if_succeed=False):
        """
        try to find the level of a long bracket, return negative level if fail
        """
        assert self._in_sequence(self._current, '[]')
        delimiter = self._current
        old_index = self._index

        level = 0
        self._take_next()
        while self._current == '=':
            level += 1
            self._take_next()

        level_not_matched = (expected_level is not None and
                             level != expected_level)
        delimiter_not_matched = self._current != delimiter
        if level_not_matched or delimiter_not_matched:
            if reset_if_fail:
                self._reset_index(old_index)
            return -1
        else:
            self._take_next()
            if reset_if_succeed:
                self._reset_index(old_index)
            return level

    _KWORDS = {
        'and',   'break', 'do',       'else', 'elseif', 'end',
        'false', 'for',   'function', 'goto', 'if',     'in',
        'local', 'nil',   'not',      'or',   'repeat', 'return',
        'then',  'true',  'until',    'while'
    }

    def _parse_word(self, allow_bool=False, allow_nil=False):
        """
        parse a word (nil, true, false, or identifier)
        """
        assert self._word_coming()

        word = self._current
        self._take_next()
        while self._current.isalnum() or self._current == '_':
            word += self._current
            self._take_next()

        not_allowed = self._KWORDS.copy()
        if allow_bool:
            not_allowed -= {'true', 'false'}
        if allow_nil:
            not_allowed -= {'nil'}
        if word in not_allowed:
            raise SyntaxError("bad word: '%s' not allowed here" % word)

        if word in {'true', 'false'}:
            return True if word == 'true' else False
        elif word in {'nil'}:
            return None
        else:
            return word

    def _equal_behind_word(self):
        """
        check whether there is a '=' behind the current word
        """
        assert self._word_coming()
        old_index = self._index
        word = self._parse_word(allow_bool=True, allow_nil=True)
        self._skip_spaces()
        equal_behind = True if self._current == '=' else False
        self._reset_index(old_index)
        return equal_behind

    def parse_table(self):
        """
        parse a table to a dict or a list
        """
        assert self._table_coming()
        self._take_next()  # for '{'

        table = {}
        count = {'rec': 0, 'lst': 0}  # number of record and list elements
        self._skip_spaces()
        while self._current != self._NOMORE:
            if self._current == '}':
                self._take_next()
                return self._finalize_table(table, count)
            else:
                self._parse_field(table, count)
                self._skip_spaces()
                if self._current == '}':
                    continue  # will finish in the next loop
                elif self._in_sequence(self._current, ',;'):
                    self._take_next()
                else:
                    raise SyntaxError("bad table: unexpected '%s'" %
                                      self._current)
                self._skip_spaces()
        raise SyntaxError("bad table: expect '}'")

    def _parse_field(self, table, count):
        """
        parse a record-style field or a list-style field
        recfield ::= ‘[’ exp ‘]’ ‘=’ exp | Name ‘=’ exp
        lstfield ::= exp
        """
        record_style1 = self._current == '[' and not self._long_string_coming()
        record_style2 = self._word_coming() and self._equal_behind_word()
        is_record_field = record_style1 or record_style2
        if is_record_field:
            key, value = self._parse_record_field()
            if value is not None:  # only insert not nil value
                table[key] = value
                count['rec'] += 1
        else:
            # nil may need further processing if the current table is a dict
            value = self._parse_expression()
            count['lst'] += 1
            table[count['lst']] = value

    def _parse_record_field(self):
        """
        parse a record field
        recfield ::= ‘[’ exp ‘]’ ‘=’ exp | Name ‘=’ exp
        """
        if self._current == '[':
            self._take_next()
            key = self._parse_expression()  # need to check nil
            if key is None:
                raise SyntaxError('bad table: table index is nil')
            self._skip_spaces()
            if self._current != ']':
                raise SyntaxError("bad table: record filed expect ']'")
            self._take_next()
        else:
            key = self._parse_word(allow_bool=False, allow_nil=False)

        self._skip_spaces()
        if self._current != '=':
            raise SyntaxError("bad table: record filed expect '='")
        self._take_next()

        self._skip_spaces()
        value = self._parse_expression()

        return key, value

    def _finalize_table(self, table, count):
        """
        convert dict to list if no record field occurred
        """
        if count['rec'] == 0:  # list fields only, convert to a list
            result = []
            for i in range(count['lst']):
                result.append(table[i + 1])
            return result
        else:                  # filter out nil values in the dict
            result = {}
            for key, value in table.items():
                if value is not None:
                    result[key] = value
            return result

    def _parse_expression(self):
        """
        (strictly) parse a nil, boolean, number, string, or table
        """
        assert not self._comment_coming()

        if self._word_coming():                 # [_a-zA-Z]
            word = self._parse_word(allow_bool=True, allow_nil=True)
            if word not in {None, True, False}:
                raise SyntaxError("bad expression: unexpected word '%s'" % word)
            return word
        elif self._current == '-':              # -, not comment, as asserted
            self._take_next()
            self._skip_spaces()
            if self._number_coming():           # negative number
                return -1 * self.parse_number()
            else:
                raise SyntaxError("bad expression: unexpected '-'")
        elif self._number_coming():             # [0-9] or .[0-9]
            return self.parse_number()
        elif self._string_coming():             # ' or "
            return self.parse_string()
        elif self._long_string_coming():        # [= or [[
            return self.parse_long_string()
        elif self._table_coming():              # {
            return self.parse_table()
        else:
            raise SyntaxError("bad expression: unexpected '%s'" % self._current)

    def parse_value(self):
        """
        parse a normal value of types nil, boolean, number, string, or table
        handle spaces and comments automatically
        """
        self._skip_spaces()
        value = self._parse_expression()
        self._skip_spaces()
        if self._current != self._NOMORE:
            raise SyntaxError("unexpected '%s'" % self._current)
        return value

def fromlua(src):
    """
    return a reconstituted object from the given Lua object representation
    """
    if not isinstance(src, str):
        raise TypeError('require a string to parse')
    parser = Parser(src)
    return parser.parse_value()
