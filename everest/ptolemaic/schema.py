###############################################################################
''''''
###############################################################################


from everest.ptolemaic.eidos import Eidos as _Eidos
from everest.ptolemaic.ephemera import Folio as _Folio


class Schema(_Eidos):

    ...


class SchemaBase(metaclass=Schema):

    @classmethod
    def make_folio(cls, /):
        return _Folio

    @classmethod
    def __class_call__(cls, /):
        super().__class_call__()
        cls.make_folio()


###############################################################################
###############################################################################
