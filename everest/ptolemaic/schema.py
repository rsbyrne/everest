###############################################################################
''''''
###############################################################################


from everest.utilities import caching as _caching, Slc as _Slc

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.eidos import Eidos as _Eidos
from everest.ptolemaic.fundaments.brace import Brace as _Brace
from everest.ptolemaic.sig import Sig as _Sig


class Schema(_Eidos):

    ...


class SchemaBase(metaclass=Schema):


    class Oid(metaclass=_Essence):

        @property
        @_caching.soft_cache()
        def sig(self, /):
            chora = self.chora.choras[0]
            return self.subject.sig.__incise_slyce__(chora)

        def __incise_retrieve__(self, incisor, /):
            inc0, *incn = incisor
            params = self.sig.__incise_retrieve__(inc0)
            basis = self.subject.instantiate(params)
            if incn:
                raise NotImplementedError
                # return basis.enspace(*incn)
            return basis


    @classmethod
    def _class_choras(cls, /):
        return dict(
            sig=cls.sig.__incision_manager__,
            )

    @classmethod
    def _make_oid(cls, /):
        return cls.Oid(_Brace[{
            key: _Slc[::val] for key, val in cls._class_choras().items()
            }])


###############################################################################
###############################################################################
