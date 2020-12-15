import numbers
import numpy as np

from ptolemaic.frames.indexable import Indexable
from datalike.structures.series import TimeSeries

class Chronable(Indexable):

    @classmethod
    def _class_construct(cls):
        super()._class_construct()
        class Case(cls.Case):
            class Storage(TimeSeries, cls.Case.Storage):
                ...
        cls.Case = Case

    def __init__(self,
            _indices = None,
            **kwargs
            ):
        _indices = [] if _indices is None else _indices
        var = self.IndexVar(
            np.float32,
            compType = numbers.Real,
            name = 'chron',
            )
        _indices.append(var)
        super().__init__(
            _indices = _indices,
            **kwargs
            )
