###############################################################################
''''''
###############################################################################


from everest.utilities.misc import ARITHMOPS as _ARITHMOPS, REVOPS as _REVOPS
from everest.incision import INCISABLEMETHS as _INCISABLEMETHS

from everest.ptolemaic.essence import Essence as _Essence

from .algebraic import ALGEBRAICMETHODS as _ALGEBRAICMETHODS

from .chora import Chora as _Chora


# _INCISIONMETHS_ = (
#     'incise', 'incise_trivial', 'incise_retrieve',
#     'incise_slyce', 'incise_fail',
#     'incise_degenerate', 'incise_empty', 'incise_contains',
#     'incise_includes', 'incise_length', 'incise_iter', 'incision_manager',
#     'armature_brace', 'armature_truss',
#     'armature_generic', 'armature_variable',
#     )


BYTHOSMETHODS = (
    *_INCISABLEMETHS, *_ALGEBRAICMETHODS, *_ARITHMOPS, *_REVOPS
    )


@_Chora.register
class Bythos(_Essence):

    for methname in BYTHOSMETHODS:
        exec('\n'.join((
            f"@property",
            f"def {methname}(cls, /):",
            f"    try:",
            f"        return cls.__class_{methname.strip('_')}__",
            f"    except AttributeError:",
            f"        try:",
            f"            return cls.__class_incision_manager__.{methname}",
            f"        except AttributeError:",
            f"            raise NotImplementedError",
            )))
    del methname

    @property
    def __incision_manager__(cls, /):
        return cls.__class_incision_manager__


class BythosBase(metaclass=Bythos):

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__class_incise_trivial__ = lambda: cls

    # Doesn't need to be decorated with classmethod for some reason:
    def __class_getitem__(cls, arg, /):
        return cls.__incise__(arg, caller=cls)   


###############################################################################
###############################################################################


#     for methname in ('mod', 'matmul'):
#         for prefix in ('', 'r'):
#             exec('\n'.join((
#                 f"def __class_{prefix}{methname}__(cls, /, *args, **kwargs):",
#                 (f"    return cls.__class_incision_manager__"
#                      f".__{prefix}{methname}__(*args, **kwargs)"),
#                 )))
#     del methname, prefix
