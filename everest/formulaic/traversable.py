###############################################################################
''''''
###############################################################################


import functools as _functools

from everest.utilities import caching as _caching

from everest.ptolemaic.compound import Compound as _Compound
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.atlantean import Kwargs as _Kwargs

from everest.algebraic import chora as _chora
from everest.algebraic.eidos import Eidos as _Eidos
from everest.algebraic.floatt import Floatt as _Floatt
from everest.algebraic.brace import Brace as _Brace

from everest.uniplex.table import Table as _Table

from .schema import Schema as _Schema


class Traversable(_chora.ChainChora, metaclass=_Schema):


    MROCLASSES = (
        'Instrument', 'Slyce', 'Case', 'Line', 'Traverse', 'Stage'
        )

    casespace: _chora.Chora
    statespace: _chora.Chora
    indexspace: _chora.Chora
    solver: object

    @property
    def __incision_manager__(self, /):
        return _Brace[_Kwargs({
            key: val for key, val in self.fields.items()
            if isinstance(val, _chora.Chora)
            })]

    def __incise_slyce__(self, incisor: _Brace.Oid, /):
        cs, st, ix = incisor.choras
        if incisor.active == (False, False, True):
            case = self.Case(self, cs.retrieve())
            line = self.Line(case, st.retrieve())
            return self.Traverse(line, ix)
        return self.Slyce(incisor)

    def __incise_retrieve__(self, incisor: _Brace, /):
        cs, st, ix = incisor
        case = self.Case(self, cs)
        line = self.Line(case, st)
        return self.Line(line, ix)


    class Instrument(metaclass=_Compound):
        ...


    class Slyce(_chora.ChainChora, metaclass=_Essence):

        OVERCLASSES = ('Instrument',)

        compound: 'owner'
        chora: _Brace

        @property
        def __incision_manager__(self, /):
            return self.chora

        @property
        def __incise_slyce__(self, /):
            return self.compound.__incise_slyce__

        @property
        def __incise_retrieve__(self, /):
            return self.compound.__incise_retrieve__


    class Case(_chora.ChainChora, metaclass=_Essence):

        OVERCLASSES = ('Instrument',)

        compound: 'owner'
        data: _Brace

        @property
        def __incision_manager__(self, /):
            return self.data

        @property
        @_caching.soft_cache()
        def plexon(self, /):
            return self.compound.plexon.folio(self.hashID)


    class Line(_chora.ChainChora, metaclass=_Essence):

        OVERCLASSES = ('Instrument',)

        case: 'owner.Case'
        initial: object

        __req_slots__ = ('indextable', 'statetable')

        @property
        def compound(self, /):
            return self.case.compound

        @property
        def __incision_manager__(self, /):
            return self.compound.indexspace

        def __incise_slyce__(self, incisor, /):
            return self.compound.Traverse(self, incisor)

        def __incise_retrieve__(self, incisor, /):
            return self.compound.Stage(self, incisor)

        @property
        @_caching.soft_cache()
        def plexon(self, /):
            sup = self.case.plexon
            axle = sup.axle(self.hashID)
            indexspace = self.compound.indexspace
            statespace = self.compound.statespace
            with self.mutable:
                self.indextable = \
                    axle.table('index', (), dtype=indexspace.dtype)
                self.statetable = \
                    axle.table('state', statespace.shape, statespace.dtype)
            return axle


    class Traverse(_chora.ChainChora, metaclass=_Essence):

        OVERCLASSES = ('Instrument',)

        line: 'owner.Line'
        interval: object

        @property
        def compound(self, /):
            return self.line.compound

        @property
        def __incision_manager__(self, /):
            return self.interval

        def __incise_slyce__(self, incisor, /):
            return self.compound.Traverse(self.line, incisor)

        def __incise_retrieve__(self, incisor, /):
            return self.compound.Stage(self.line, incisor)

        def solve(self, /):
            return self.compound.solver(self)

        def store(self, /):
            data = self.solve()
            inds = data.t
            vertices = data.y.T
            indtable = self.table.sub('index')


    class Stage(metaclass=_Essence):

        OVERCLASSES = ('Instrument',)

        line: 'owner.Line'
        index: object

        @property
        def compound(self, /):
            return self.line.compound

        def solve(self, /):
            return self.compound.solver(self)

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



    # __req_slots__ = ('outspace',)

    # def __init__(self, /):
    #     super().__init__()
    #     self.outspace = _Brace[_Kwargs(
    #         index=self.indexspace, state=self.statespace
    #         )]