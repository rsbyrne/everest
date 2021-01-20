from ._base import _Vanishable, _Colourable
from .edges import Edges
from .grid import Grid
from .ticks import Ticks

class _PropsController(_Vanishable, _Colourable):
    pass

class Props(_PropsController):
    def __init__(self,
            mplax,
            dims = ('x', 'y'),
            colour = 'black',
            visible = True,
            ):
        grid = Grid(
            mplax,
            dims = dims,
            colour = 'grey',
            alpha = 0.5,
            )
        ticks = Ticks(
            mplax,
            dims = dims,
            )
        edges = Edges(
            mplax,
            dims = dims,
            )
        super().__init__(
            mplax,
            colour = colour,
            visible = visible,
            )
        self._add_sub(grid, 'grid')
        self._add_sub(ticks, 'ticks')
        self._add_sub(edges, 'edges')
        for dim in dims:
            edges[dim]._add_sub(ticks[dim], 'ticks')
            edges[dim]['primary']._add_sub(ticks[dim], 'ticks')