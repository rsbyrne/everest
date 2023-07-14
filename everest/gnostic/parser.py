###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import deque as _deque


from . import tree as _tree


class ParserException(Exception):

    ...


class ParserBase(metaclass=_abc.ABCMeta):

    def __init__(self, /):
        self.buffer = _deque()

    @_abc.abstractmethod
    def __call__(self, stream, /) -> _tree.Node:
        raise NotImplementedError


class SubParser(ParserBase):

    def __init__(self, previous, /):
        self.previous = previous


class DelimitedParser(SubParser):

    opener = None
    closer = None
    nodetyp = None

    def process(self, character, /):
        self.buffer.append(character)

    def finalise(self, /):
        if (buffer := self.buffer):
            return self.nodetyp(self.buffer)
        return _tree.Null

    def __call__(self, stream, /):
        for character in stream:
            if character == self.closer:
                break
            self.process(character)
        else:
            raise ParserException
        return self.finalise()


class SlugParser(DelimitedParser):

    opener = "'"
    closer = "'"
    nodetyp = _tree.Slug


class ExpressionParser(SubParser):

    def __call__(self, stream, /):
        try:
            char = next(stream)
        except StopIteration:
            return _tree.NULL
        if char == SlugParser.opener:
            return SlugParser()(stream)
        if char == CellParser.opener:
            return CellParser()(stream)
        buffer = self.buffer
        for character in stream:
            buffer.append(character)
        return _tree.Expression(buffer)


class CellParser(SubParser):

    opener = '{'
    closer = '}'

    def __call__(self, stream, /):
        try:
            char = next(stream)
        except StopIteration:
            return _tree.NULL
        


class Parser(ParserBase):

    def __call__(self, stream, /):
        parser = GeneralParser(self)
        return parser(stream)


###############################################################################
###############################################################################


# class StatementParser(SubParser):

#     __slots__ = ('interface', 'query', 'value')

#     def __call__(self, stream, /):
#         chars = ['=', ':']
#         self.interface = _tree.Null
#         for character in stream:
#             if character == '=':
#                 self.query = ExpressionParser()(self.buffer)
#                 break
#         else:
#             self.value = ExpressionParser()(self.buffer)


# class CellParser(DelimitedParser):

#     terminator = '}'
#     nodetyp = _tree.Cell
#     lineending = ';'

#     __slots__ = ('statements',)

#     def __init__(self, /):
#         super().__init__()
#         self.statements = _deque()

#     def add_statement(self, /)
#         buffer = self.buffer
#         statement = StatementParser()(buffer)
#         buffer.clear()
#         self.statements.append(statement)

#     def process(self, character, /):
#         if character == self.lineending:
#             self.add_statement()

#     def finalise(self, /):
#         if (buffer := self.buffer):
#             self.add_statement()
#         return self.nodetyp(*self.statements)