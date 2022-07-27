###############################################################################
''''''
###############################################################################


import types as _types
from collections import abc as _collabc

from everest.ptolemaic.ousia import Binding as _Binding
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.compound import Compound as _Compound


class Query(metaclass=_Essence):
    ...


# class ThinQuery()


class Sample(Query, metaclass=_Compound):

    content: object = None


class Bounds(Query, metaclass=_Compound):

    lower: object = None
    upper: object = None

    def __iter__(self, /):
        yield self.lower
        yield self.upper


class Shallow(Query, metaclass=_Compound):

    query: object


###############################################################################
###############################################################################
