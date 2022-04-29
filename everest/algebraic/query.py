###############################################################################
''''''
###############################################################################


import types as _types
from collections import abc as _collabc

from everest.ptolemaic.atlantean import Diict as _Diict
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.schematic import Schematic as _Schematic


class Query(metaclass=_Essence):
    ...


# class ThinQuery()


class Sample(Query, metaclass=_Schematic):

    content: object = None


class Bounds(Query, metaclass=_Schematic):

    lower: object = None
    upper: object = None

    def __iter__(self, /):
        yield self.lower
        yield self.upper


class Shallow(Query, metaclass=_Schematic):

    query: object


###############################################################################
###############################################################################
