###############################################################################
''''''
###############################################################################


import abc as _abc
from enum import Enum as _Enum


class Node(metaclass=_abc.ABCMeta):

    @_abc.abstractmethod
    def _content_repr_(self, /) -> str:
        raise NotImplementedError

    def __repr__(self, /):
        return f"<{type(self).__name__}:{self._content_repr_()}>"

    @classmethod
    def convert(cls, arg, /):
        if isinstance(arg, cls):
            return arg
        return cls(arg)


@Node.register
class Special(_Enum):

    NULL = 0

    @classmethod
    def convert(cls, _, /):
        raise NotImplementedError
    


class Slug(Node):

    def __init__(self, buffer, /):
        self.content = ''.join(buffer)

    def _content_repr_(self, /):
        return repr(self.content)


class Expression(Node):

    def __init__(self, buffer, /):
        self.content = ''.join(buffer)

    def _content_repr_(self, /):
        return repr(self.content)


class Interface(_Enum):

    INTERIOR = 0
    EXTERIOR = 1
    QUERY = 2


class Statement(Node):

    def __init__(self, interface, query, value, /):
        self.interface = Interace[interface]
        self.query, self.value = map(
            Expression.convert,
            (query, value),
            )


class Cell(Node):

    def __init__(self, /, *statements):
        self.statements = tuple(map(Statement.convert, statements))


###############################################################################
###############################################################################
