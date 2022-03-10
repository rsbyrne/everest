###############################################################################
''''''
###############################################################################


from everest.utilities import misc as _misc

from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    IncisionHandler as _IncisionHandler,
    Incisable as _Incisable,
    )

from .essence import Essence as _Essence


_INCISIONMETHS_ = (
    'incise', 'incise_trivial', 'incise_retrieve',
    'incise_slyce', 'incise_fail',
    'incise_degenerate', 'incise_empty', 'incise_contains',
    'incise_includes', 'incise_length', 'incise_iter', 'incision_manager',
    'armature_brace', 'armature_truss',
    'armature_generic', 'armature_variable',
    )


@_Incisable.register
class Bythos(_Essence):

    @property
    def __contains__(cls, /):
        return _IncisionProtocol.CONTAINS(cls)

    @property
    def __includes__(cls, /):
        return _IncisionProtocol.INCLUDES(cls)

    @property
    def __len__(cls, /):
        return _IncisionProtocol.LENGTH(cls)

    def __bool__(cls, /):
        return True

    @property
    def __iter__(cls, /):
        return _IncisionProtocol.ITER(cls)

    for methname in (*_misc.ARITHMOPS, *_misc.REVOPS):
        exec('\n'.join((
            f"def __{methname}__(cls, /, *args, **kwargs):",
            f"    try:",
            f"        meth = cls.__class_{methname}__",
            f"    except AttributeError:",
            f"        return NotImplemented",
            f"    return meth(*args, **kwargs)",
            )))
    for methname in _INCISIONMETHS_:
        exec('\n'.join((
            f"@property",
            f"def __{methname}__(cls, /):",
            f"    return cls.__class_{methname}__",
            )))
    del methname


class BythosBase(metaclass=Bythos):

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__class_incise_trivial__ = lambda: cls

    # Doesn't need to be decorated with classmethod for some reason:
    def __class_getitem__(cls, arg, /):
        return _IncisionProtocol.INCISE(cls)(arg, caller=cls)


###############################################################################
###############################################################################
