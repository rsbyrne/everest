###############################################################################
''''''
###############################################################################


import itertools as _itertools


from .ptolemaic import Ptolemaic as _Ptolemaic
from .eidos import Eidos as _Eidos
from .primitive import Primitive as _Primitive


class Sprite(_Ptolemaic, metaclass=_Eidos):

    class BadParameter(Exception):

        def message(self, /):
            yield from super().message()
            yield ''.join((
                "Note that this class only accepts inputs which are Primitives",
                " (e.g. Python int, float, bool)"
                ))

    @classmethod
    def check_param(cls, arg, /):
        if isinstance(arg, _Primitive):
            return arg
        raise cls.BadParameter(arg)


###############################################################################
###############################################################################
