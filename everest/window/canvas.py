from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from ._fig import Fig as _Fig
from .ax import Ax

class Canvas(_Fig):

    def __init__(self,
            name = None,
            title = None,
            shape = (1, 1),
            size = (3, 3), # inches
            dpi = 100, # pixels per inch
            facecolour = 'white',
            edgecolour = 'black',
            **kwargs
            ):

        fig = Figure(
            figsize = size,
            dpi = dpi,
            facecolor = facecolour,
            edgecolor = edgecolour,
            **kwargs
            )

        nrows, ncols = shape

        self.shape = shape
        self.nrows, self.ncols = nrows, ncols
        self.size = size

        self._updateFns = []
        self.fig = fig

        self.clear()

        self.ax = self.make_ax

        if not title is None:
            self.set_title(title)

        super().__init__()

    def set_title(self, title, fontsize = 16):
        self.title = title
        self.fig.suptitle(title, fontsize = fontsize)

    def make_ax(self, place = (0, 0), superimpose = False, **kwargs):
        rowNo, colNo = place
        index = self._calc_index(place)
        axObj = Ax(self, index = index, **kwargs)
        self.axs[rowNo][colNo].append(axObj)
        return axObj

    def clear(self):
        self.fig.clf()
        self.axs = [
            [[] for col in range(self.ncols)] \
                for row in range(self.nrows)
            ]

    def _calc_index(self, place):
        rowNo, colNo = place
        if colNo >= self.shape[1] or rowNo >= self.shape[0]:
            raise ValueError("Prescribed row and col do not exist.")
        return (self.ncols * rowNo + colNo)

    def _update(self):
        for fn in self._updateFns:
            fn()

    def _save(self, filepath):
        self.fig.savefig(filepath)

    def _show(self):
        FigureCanvas(self.fig)
        return self.fig
