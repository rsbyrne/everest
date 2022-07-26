###############################################################################
''''''
###############################################################################


from everest.utilities import pretty as _pretty

from .enumm import Enumm as _Enumm
from .sprite import Sprite as _Sprite


class Semaphore(_Enumm):

    @classmethod
    def _yield_mroclasses(meta, /):
        yield from super()._yield_mroclasses()
        yield 'Dispatch', ()


class Dispatch(metaclass=_Sprite):

    envelope: object
    content: object = None

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        if params.envelope not in cls.__corpus__.enumerators:
            raise ValueError(params.envelope)
        return params

    def _repr_pretty_(self, p, cycle, /, root=None):
        return _pretty.pretty_call(
            self.envelope, ((self.content,), {}), p, cycle, root=root
            )


class _SemaphoreBase_(metaclass=Semaphore):

    Dispatch = Dispatch

    def __call__(self, content, /):
        return self.Dispatch(self, content)


###############################################################################
###############################################################################