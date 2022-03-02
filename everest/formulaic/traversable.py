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
    Multi as _Multi,
    )
from everest.algebraic.eidos import Eidos as _Eidos
from everest.algebraic.floatt import Floatt as _Floatt
from everest.algebraic.brace import Brace as _Brace

from everest.uniplex.table import Table as _Table

from .schema import Schema as _Schema


class Traversable(_ChainChora, metaclass=_Schema):


    MROCLASSES = ('Slyce', 'Instruments')

    casespace: _Chora
    statespace: _Chora
    indexspace: _Chora
    solver: object

    @property
    def schematic(self, /):
        return self

    @property
    def __incision_manager__(self, /):
        return _Brace[_Kwargs({
            key: val for key, val in self.params.items()
            if isinstance(val, _Chora)
            })]

    def __incise_slyce__(self, incisor: _Brace.Oid, /):
        cs, st, ix = incisor.choras
        schematic = self.schematic
        if incisor.active == (False, False, True):
            case = schematic.Instruments.Case(schematic, cs.retrieve())
            line = schematic.Instruments.Line(case, st.retrieve())
            return schematic.Instruments.Traverse(line, ix)
        return schematic.Instruments.Slyce(incisor)

    def __incise_retrieve__(self, incisor: _Brace, /):
        cs, st, ix = incisor
        schematic = self.schematic
        case = schematic.Instruments.Case(schematic = cs)
        line = schematic.Instruments.Line(case, st)
        return schematic.Instruements.Line(line, ix)

    # def _repr_pretty_(self, p, cycle, root=None):
    #     if root is None:
    #         root = self._ptolemaic_class__.__qualname__
    #     p.text(f'{root}({self.hashID})')


    class Instruments(metaclass=_Sprite):

        SUBCLASSES = ('Slyce', 'Case', 'Line', 'Traverse', 'Stage')

        @property
        def folio(self, /):
            return self.schematic.folio


        class Slyce(_ChainChora, metaclass=_Essence):

            schematic: 'owner'
            chora: _Brace

            @property
            def __incision_manager__(self, /):
                return self.chora

            @property
            def __incise_slyce__(self, /):
                return self.schematic.__incise_slyce__

            @property
            def __incise_retrieve__(self, /):
                return self.schematic.__incise_retrieve__


        class Case(_ChainChora, metaclass=_Essence):

            schematic: 'owner'
            data: _Brace

            @property
            def __incision_manager__(self, /):
                return self.data

            @property
            def folio(self, /):
                return self.schematic.folio.folio(self.hashID)


        class Line(_ChainChora, metaclass=_Essence):

            case: 'owner.Instruments.Case'
            initial: object

            @property
            def schematic(self, /):
                return self.case.schematic

            @property
            def __incision_manager__(self, /):
                return self.schematic.indexspace

            def __incise_slyce__(self, incisor, /):
                return self.schematic.Instruments.Traverse(self, incisor)

            def __incise_retrieve__(self, incisor, /):
                return self.schematic.Instruments.Stage(self, incisor)

            @property
            def folio(self, /):
                return self.case.folio.folio(self.hashID)

            @property
            def data(self, /):
                axle = self.folio.axle(self.hashID)
                return (
                    axle.table('index', dtype=float),
                    axle.table('state', dtype=float),
                    )


        class Traverse(_ChainChora, metaclass=_Essence):

            line: 'owner.Instruments.Line'
            interval: object

            @property
            def schematic(self, /):
                return self.line.schematic

            @property
            def __incision_manager__(self, /):
                return self.interval

            def __incise_slyce__(self, incisor, /):
                return self.schematic.Instruments.Traverse(self.line, incisor)

            def __incise_retrieve__(self, incisor, /):
                return self.schematic.Instruments.Stage(self.line, incisor)

            def solve(self, /):
                return self.schematic.solver(self)

            def store(self, /):
                data = self.solve()
                inds = data.t
                vertices = data.y.T
                indtable = self.table.sub('index')


        class Stage(metaclass=_Essence):

            line: 'owner.Instruments.Line'
            index: object

            @property
            def schematic(self, /):
                return self.line.schematic

            def solve(self, /):
                return self.schematic.solver(self)

            @property
            def folio(self, /):
                return self.line.folio


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
