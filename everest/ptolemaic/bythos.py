###############################################################################
''''''
###############################################################################


import functools as _functools

from everest.ptolemaic.chora import Incisable as _Incisable

from everest.ptolemaic.essence import Essence as _Essence


class Bythos(_Essence):

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(cls, 'chora'):
            raise RuntimeError(
                "Classes inheriting from `Bythos` must provide a chora."
                )

    def incise(cls, chora, /):
        return _Incisable.incise(cls, chora)

    def retrieve(cls, index, /):
        return _Incisable.retrieve(cls, index)

    def trivial(cls, chora, /):
        return _Incisable.trivial(cls, chora)

    def fail(cls, /, *args):
        return _Incisable.fail(cls, *args)

    def __getitem__(cls, arg, /, *, caller=None):
        return _Incisable.__getitem__(cls, arg, caller=caller)


###############################################################################
###############################################################################
