###############################################################################
''''''
###############################################################################


import types as _types
from collections import abc as _collabc

from everest.ptolemaic.diict import Diict as _Diict
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.pentheros import Pentheros as _Pentheros


class Query(metaclass=_Essence):
    ...


# class ThinQuery()


class Sample(Query, metaclass=_Pentheros):

    content: object = None


class Bounds(Query, metaclass=_Pentheros):

    lower: object = None
    upper: object = None

    def __iter__(self, /):
        yield self.lower
        yield self.upper


class Shallow(Query, metaclass=_Pentheros):

    query: object


###############################################################################
###############################################################################
