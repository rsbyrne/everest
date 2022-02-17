###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.ptolemaic.eidos import Eidos as _Eidos
from everest.ptolemaic.ephemera import Folio as _Folio


class Schema(_Eidos):

    ...


class SchemaBase(metaclass=Schema):
    ...

    # @classmethod
    # def __class_init__(cls, /):
    #     super().__class_init__()
    #     cls.folio = _Folio()

    # @classmethod
    # def instantiate(cls, params, /):
    #     obj = super().instantiate(params)
    #     obj


###############################################################################
###############################################################################
