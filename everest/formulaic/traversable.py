###############################################################################
''''''
###############################################################################


import functools as _functools

from everest.incision import IncisionProtocol as _IncisionProtocol
from everest.utilities import caching as _caching

from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.diict import Kwargs as _Kwargs

from everest.algebraic.chora import (
    Chora as _Chora,
    Slyce as _Slyce,
    ChainChora as _ChainChora,
    Degenerate as _Degenerate,
    )
from everest.algebraic.eidos import Eidos as _Eidos
from everest.algebraic.floatt import Floatt as _Floatt
from everest.algebraic.brace import Brace as _Brace

from .schema import Schema as _Schema


class Traversable(_Chora, metaclass=_Schema):


    MROCLASSES = ('Slyce', 'Instruments')

    casespace: _Chora
    statespace: _Chora
    indexspace: _Chora
    solver: object

    @classmethod
    def __class_init__(cls, /):

        super().__class_init__()

        for name in cls.Instruments.SUBCLASSES:

            @_functools.wraps(getattr(cls.Instruments, name).__call__)
            def method(self, /, *args, _name_=name, **kwargs):
                return getattr(self.Instruments, _name_)(
                    self, *args, **kwargs
                    )

            setattr(cls, name.lower(), method)

        def slyce(self, /, *args, **kwargs):
            return self.Slyce(self, *args, **kwargs)

        cls.slyce = slyce

    @property
    def __incision_manager__(self, /):
        return self.slyce(self.casespace, self.statespace, self.indexspace)


    class Slyce(_ChainChora, metaclass=_Sprite):

        schematic: object
        casespace: object
        statespace: object
        indexspace: object

        @property
        @_caching.soft_cache()
        def __incision_manager__(self, /):
            return _Brace[_Kwargs(
                casespace=self.casespace,
                statespace=self.statespace,
                indexspace=self.indexspace,
                )]

        def __incise_slyce__(self, incisor: _Brace.Oid, /):
            cs, st, ix = incisor.choras
            schematic = self.schematic
            if incisor.active == (False, False, True):
                return schematic.traverse(cs.retrieve(), st.retrieve(), ix)
            out = schematic.slyce(*incisor.choras)
            out.softcache['__incision_manager__'] = incisor
            return out

        def __incise_retrieve__(self, incisor: _Brace, /):
            return self.schematic.stage(*incisor)


    class Instruments(metaclass=_Sprite):


        SUBCLASSES = ('Line', 'Traverse', 'Stage')

        schematic: 'owner'


        class Line(_ChainChora, metaclass=_Essence):

            case: object
            initial: object

            @property
            def __incision_manager__(self, /):
                return self.schematic.indexspace

            def __incise_slyce__(self, incisor, /):
                return self.schematic.traverse(
                    self.case, self.initial, incisor
                    )

            def __incise_retrieve__(self, incisor, /):
                return self.schematic.stage(self.case, self.initial, incisor)


        class Traverse(_ChainChora, metaclass=_Essence):

            case: object
            initial: object
            interval: object

            @property
            def __incision_manager__(self, /):
                return self.interval

            def __incise_slyce__(self, incisor, /):
                return self.schematic.traverse(
                    self.case, self.initial, incisor
                    )

            def __incise_retrieve__(self, incisor, /):
                return self.schematic.stage(self.case, self.initial, incisor)

            def solve(self, /):
                return self.schematic.solver(self)


        class Stage(metaclass=_Essence):

            case: object
            initial: object
            index: object

            def solve(self, /):
                return self.schematic.solver(self)


###############################################################################
###############################################################################


#     class Case(metaclass=_Eidos):

#         a: _Floatt
#         b: _Floatt
#         c: _Floatt


#     class Config(metaclass=_Eidos):

#         x: _Floatt
#         y: _Floatt
#         z: _Floatt


#     class Metric(metaclass=_Eidos):

#         chron: _Floatt
