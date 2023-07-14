###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import deque as _deque
from enum import Enum as _Enum
import itertools as _itertools

from . import tree as _tree


class TokeniserException(Exception):

    ...


class Token:

    __slots__ = ('typ', 'value')

    def __init__(self, typ, value, /):
        self.typ, self.value = typ, value

    def __iter__(self, /):
        return self.typ, self.value

    def __repr__(self, /):
        return f"< {self.typ} '{self.value}' >"


class TokenType(_Enum):

    def __call__(self, /, *values):
        return Token(self, ''.join(values))


class Tokens(TokenType):

    SLUG = 0


class Simple(TokenType):

    ...


class Flow(Simple):

    EOL = ';'


class EnclosureType(Simple):

    ...


class Cell(EnclosureType):

    HEAD = '{'
    TAIL = '}'


class Bracket(EnclosureType):

    HEAD = '('
    TAIL = ')'


class Square(EnclosureType):

    HEAD = '['
    TAIL = ']'


class Interface(TokenType):

    INTERIOR = '='
    EXTERIOR = '!'
    QUERY = ':'


SIMPLE = {
    **{token.value: token for token in _itertools.chain(
        Flow, Cell, Bracket, Square, Interface,
        )},
    }


class TokeniserBase(metaclass=_abc.ABCMeta):

    def __init__(self, stream, /):
        self.stream = iter(stream)
        self.stopped = False
        self.delegated = iter(())

    @_abc.abstractmethod
    def _next_(self, /):
        raise NotImplementedError

    def __next__(self, /):
        if self.stopped:
            raise StopIteration
        try:
            return next(self.delegated)
        except StopIteration:
            out = self._next_()
            if out is None:
                raise StopIteration
            if isinstance(out, Token):
                return out
            self.delegated = out
            return next(out)

    def __iter__(self, /):
        return self


class StringTokeniser(TokeniserBase):

    delimiter = "'"

    def _next_(self, /):
        buffer, delimiter = _deque(), self.delimiter
        for char in self.stream:
            if char == delimiter:
                self.stopped = True
                return Tokens.SLUG(*buffer)
            buffer.append(char)
        if buffer:
            raise TokeniserException(
                "Stream ended without closing a string."
                )


class SimpleTokeniser(TokeniserBase):

    def _next_(self, /):
        for char in self.stream:
            if char.isspace():
                continue
            try:
                tokentype = SIMPLE[char]
            except KeyError:
                pass
            else:
                return tokentype(char)
            if char == "'":
                return StringTokeniser(stream)
            raise TokeniserException(char)


class IndentTokeniser(TokeniserBase):

    def __init__(self, stream, indent, /):
        super().__init__(stream)
        self.indent = indent

    def _next_(self, /):
        buffer = _deque()
        for char in self.stream:
            if char.isspace():
                if char == '\n':
                    buffer.clear()
                else:
                    buffer.append(char)
                continue
            indent = ''.join(buffer)
            selfdent = self.indent
            if indent == selfdent:
                
                


# class IndentTokeniser(TokeniserBase):

#     def __init__(self, indent, /):
#         if not indent:
#             raise ValueError("An indent of non-zero length must be specified.")
#         self.indent = indent
#         super().__init__()

#     def process(self, char, /):
#         buffer = self.buffer
#         if char == '\n':
#             buffer.clear()
#             return Flow.EOL()
#         if char.isspace():
#             buffer.append(char)
#             return
#         if buffer:
#             indent = ''.join(buffer)
#             buffer.clear()
#             selfdent = self.indent
#             if indent != selfdent:
#                 if indent.startswith(selfdent):
#                     return IndentTokeniser()

#     def __call__(self, stream, /):
#         for char in stream:
#             if char.isspace():
#                 out = self.process(char)
#                 if isinstance(out, Token):
#                     yield out
#                 elif isinstance(out, TokeniserBase):
#                     yield from out(stream)

#     def __call__(self, stream, /):
#         buffer = self.buffer
#         sindent = self.indent
#         for char in stream:
#             if char == '\n':
#                 buffer.clear()
#                 continue
#             if char.isspace():
#                 buffer.append(char)
#                 continue
#             if buffer:
#                 indent = ''.join(buffer)
#                 buffer.clear()
#                 if indent == sindent:
#                     yield Flow.EOL()
#                 elif indent.startswith(self.indent):
#                     yield from Tokeniser(indent)(stream)
#                     continue
#                 else:
#                     break
#                     continue
#             try:
#                 totyp = SIMPLE[char]
#             except KeyError:
#                 pass
#             else:
#                 if isinstance(totyp, EnclosureType):
#                     yield from EnclosureTokeniser(type(totyp))(stream)
#                     continue
#                 yield totyp(char)
#                 continue
#             if char == "'":
#                 yield from StringTokeniser()(stream)
#                 continue
#             raise TokeniserException(char)


###############################################################################
###############################################################################


        

    # def __call__(self, stream, /):
    #     typ = self.typ
    #     head, tail = tuple(typ)
    #     yield head()
    #     level = 1
    #     for char in stream:
    #         if char.isspace():
    #             continue
    #         try:
    #             totyp = SIMPLE[char]
    #         except KeyError:
    #             pass
    #         else:
    #             if isinstance(totyp, typ):
    #                 if totyp is head:
    #                     level += 1
    #                 elif totyp is tail:
    #                     level -= 1
    #                     if level == 0:
    #                         break
    #                 else:
    #                     assert False
    #             else:
    #                 yield totyp(char)
    #             continue
    #         if char == "'":
    #             yield from StringTokeniser()(stream)
    #             continue
    #         raise TokeniserException(char)
    #     else:
    #         missing = tail.value * level
    #         raise TokeniserException(
    #             f"Stream ended awaiting something like: '{missing}'"
    #             )
    #     yield tail()


# class Tokeniser(TokeniserBase):

#     def __call__(self, stream, /):
#         buffer = _deque()
#         yield Cell.HEAD()
#         for char in stream:
#             if char == '\n':
#                 buffer.clear()
#                 yield Flow.EOL()
#                 continue
#             if char.isspace():
#                 buffer.append(char)
#                 continue
#             raise TokeniserException(char)
