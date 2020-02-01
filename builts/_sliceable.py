from . import Built
from ..exceptions import EverestException

class SliceTypeError(EverestException):
    '''The object providing for slicing was of unexpected type.'''
    pass

class Sliceable(Built):
    def __init__(self, sliceFn, sliceType = None, **kwargs):
        self.sliceFn, self.sliceType = sliceFn, sliceType
        super().__init__(**kwargs)
    def __getitem__(self, slicer):
        if self.sliceType is None:
            return self.sliceFn(slicer)
        else:
            if isinstance(slicer, self.sliceType):
                return self.sliceFn(slicer)
            else:
                raise SliceTypeError
