from ._base import _Vanishable, _Colourable
from .axes import Axes
from .grid import Grid
from .ticks import Ticks

class _PropsController(_Vanishable, _Colourable):
    pass

class Props(_PropsController):
    def __init__(self, mplax, dims = ('x', 'y')):
        grid = Grid(mplax, dims = dims)
        ticks = Ticks(
            mplax,
            dims = dims,
            )
        axes = Axes(
            mplax,
            dims = dims,
            dimsubs = tuple(ticks[dim] for dim in dims),
            ticks = ticks,
            )
        super().__init__(
            axes = axes,
            ticks = ticks,
            grid = grid
            )