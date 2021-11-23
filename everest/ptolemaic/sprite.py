###############################################################################
''''''
###############################################################################


import hashlib as _hashlib
import itertools as _itertools

from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic
from everest.ptolemaic.inherence import Inherence as _Inherence
from everest.ptolemaic.primitive import Primitive as _Primitive


class Sprite(_Ptolemaic, metaclass=_Inherence):

    _ptolemaic_mroclasses__ = ('BadParameter', 'Registrar')
    _ptolemaic_knowntypes__ = (_Primitive,)

    BadParameters = _Inherence.BadParameters
    Registrar = _Inherence.Registrar

    @classmethod
    def parameterise(cls, register, /, *args, **kwargs):
        register(*args, **kwargs)

    def _get_hashcode(self):
        content = repr(self).encode()
        return _hashlib.md5(content).hexdigest()

    def _repr(self, /):
        args, kwargs = self.argskwargs
        return ', '.join(_itertools.chain(
            map(repr, args),
            map('='.join, zip(kwargs, map(repr, kwargs.values()))),
            ))


###############################################################################
###############################################################################
