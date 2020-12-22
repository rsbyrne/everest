import numpy as np
import math

from everest.h5anchor import disk
from .data import DataPile, DataSpread

from .utilities import unique_list
from .properties import Grid, Ticks, Axes

class Ax:

    _plotFuncs = {
        'line': 'plot',
        'scatter': 'scatter'
        }

    def __init__(self,
            canvas = None,
            index = 0,
            projection = 'rectilinear',
            name = None,
            **kwargs
            ):

        if canvas is None:
            from .canvas import Canvas
            canvas = Canvas()

        if name is None:
            name = disk.tempname()

        ax = canvas.fig.add_subplot(
            canvas.nrows,
            canvas.ncols,
            index + 1,
            projection = projection,
            label = name,
            **kwargs
            )

        # Probably need a more generic solution for this:
        if projection == '3d':
            self.dims = ('x', 'y', 'z')
            self.vol = True
        else:
            self.dims = ('x', 'y')
            self.vol = False

        self.grid = Grid(ax, self.dims)
        self.ticks = Ticks(ax, self.dims)
        self.axes = Axes(ax, self.dims)

        self.pile = DataPile()

        self.canvas, self.index, self.projection, self.name = \
            canvas, index, projection, name

        colNo = index % canvas.ncols
        rowNo = int((index - colNo) / canvas.ncols)
        self.colNo, self.rowNo = colNo, rowNo

        self.ax = ax
        self.collections = []

        self.axes.margin = 0.

        self.facecolour = None
        self.facecolourVisible = True
        axStack = self._get_axStack()
        self.facecolour = axStack[0].facecolour
        self.facecolourVisible = axStack[0].facecolourVisible
        self.set_facecolour()

    def set_facecolour(self, colour = None):
        self.ax.set_facecolor((0, 0, 0, 0))
        if colour is None:
            colour = self.facecolour
        if not self.facecolourVisible:
            setcolour = (0, 0, 0, 0)
        elif colour is None:
            setcolour = (0, 0, 0, 0)
        else:
            setcolour = colour
        axStack = self._get_axStack()
        axStack[0].ax.set_facecolor(setcolour)
        for ax in axStack:
            ax.facecolour = colour
    def toggle_facecolour(self):
        self.set_facecolour()
        axStack = self._get_axStack()
        for ax in axStack:
            ax.facecolourVisible = not self.facecolourVisible

    def _get_axStack(self):
        axStack = self.canvas.axes[self.rowNo][self.colNo]
        if len(axStack):
            return axStack
        else:
            return [self,]

    def _get_axis_screen_length(self, i, vol = False):
        # Need a better approach for this...
        if vol:
            hor, ver = (self._get_axis_screen_length(si) for si in (0, 1))
            if i in {0, 1}:
                return math.hypot(hor, ver) / 2
            else:
                return ver / 2
        else:
            return self.canvas.size[i] / self.canvas.shape[::-1][i]

    def _autoconfigure_axes(self, *args, **kwargs):
        for i, dim in enumerate(self.dims):
            self._autoconfigure_axis(
                i,
                self.pile.concatenated[dim],
                *args,
                **kwargs,
                )
    def _autoconfigure_axis(self,
            i,
            data,
            scale = 'linear',
            ticksPerInch = 1,
            alpha = 0.5,
            hide = False
            ):
        nTicks = ticksPerInch * self._get_axis_screen_length(i, vol = self.vol)
        label, tickVals, minorTickVals, tickLabels, lims = \
            data.auto_axis_configs(nTicks)
        axname = {0 : 'x', 1 : 'y', 2 : 'z'}[i]
        axis, ticks, grid = \
            self.axes[axname], self.ticks[axname], self.grid[axname]
        axis.scale = scale
        axis.lims = lims
        ticks.major.set_values_labels(tickVals, tickLabels)
        if not self.vol:
            ticks.minor.values = minorTickVals
        axis.label = label
        grid.alpha = alpha
        grid.minor.alpha = 0.5
        if hide:
            axis.visible = False

    def draw(self,
            x,
            y,
            z = None,
            /,
            c = None,
            s = None,
            l = None,
            *,
            variety = None,
            **kwargs,
            ):
        spread = DataSpread(x, y, z, c, s, l)
        self.pile.append(spread)
        self._autoconfigure_axes()
        drawFunc = getattr(self.ax, self._plotFuncs[variety])
        collection = drawFunc(
            *spread.drawArgs,
            **spread.drawKwargs,
            )
        self.collections.append(collection)

    def clear(self):
        self.ax.clear()
        self.pile.clear()
        self.collections = []

    def scatter(self, *args, **kwargs):
        self.draw(*args, variety = 'scatter', **kwargs)
    def line(self, *args, **kwargs):
        self.draw(*args, variety = 'line', **kwargs)

    def annotate(self,
            x,
            y,
            label,
            arrowProps = dict(arrowstyle = 'simple'),
            points = None,
            horizontalalignment = 'center',
            verticalalignment = 'center',
            rotation = 0,
            **kwargs
            ):
        if self.vol:
            raise Exception("Not working for 3D yet.")
        self.ax.annotate(
            label,
            (x, y),
            xytext = (10, 10) if points is None else points,
            textcoords = 'offset points',
            arrowprops = arrowProps,
            horizontalalignment = horizontalalignment,
            verticalalignment = verticalalignment,
            rotation = rotation,
            **kwargs
            )

    def show(self):
        return self.canvas.show()
