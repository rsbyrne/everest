###############################################################################
''''''
###############################################################################


from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    IncisionHandler as _IncisionHandler,
    Incisable as _Incisable,
    )

from everest.ptolemaic.essence import Essence as _Essence

from .chora import Chora as _Chora


_INCISIONMETHS_ = (
    'incise', 'incise_trivial', 'incise_retrieve',
    'incise_slyce', 'incise_fail',
    'incise_degenerate', 'incise_empty', 'incise_contains',
    'incise_includes', 'incise_length', 'incise_iter', 'incision_manager',
    'armature_brace', 'armature_truss',
    'armature_generic', 'armature_variable',
    )


# @_Incisable.register
@_Chora.register
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

    @property
    def __iter__(cls, /):
        return _IncisionProtocol.ITER(cls)

    for methname in _INCISIONMETHS_:
        exec('\n'.join((
            f"@property",
            f"def __{methname}__(cls, /):",
            f"    return cls.__class_{methname}__",
            )))
    for methname in ('mod', 'matmul'):
        for prefix in ('', 'r'):
            exec('\n'.join((
                f"def __class_{prefix}{methname}__(cls, /, *args, **kwargs):",
                (f"    return cls.__class_incision_manager__"
                     f".__{prefix}{methname}__(*args, **kwargs)"),
                )))
    del methname, prefix


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
