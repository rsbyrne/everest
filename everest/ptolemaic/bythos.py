###############################################################################
''''''
###############################################################################


import functools as _functools

from everest.ptolemaic import chora as _chora
from everest.ptolemaic.essence import Essence as _Essence


class Bythos(_Essence):

    ### Methods relating to the Incision Protocol for classes:

    def class_retrieve(cls, arg, /):
        raise NotImplementedError("Retrieval not supported on this class.")

    def class_incise(cls, arg, /):
        raise NotImplementedError("Incision not supported on this class.")

    def class_trivial(cls, arg, /):
        return cls

    def _class_defer_chora_methods(cls, /):

        chcls = cls.ClassChora
        prefixes = chcls.PREFIXES
        defkws = chcls._get_defkws((f"cls.class_{st}" for st in prefixes))

        for prefix in prefixes:
            methname = f"class_{prefix}"
            if not hasattr(cls, methname):
                setattr(cls, methname, cls._class_chora_passthrough)

        exec('\n'.join((
            f"@classmethod",
            f"def _chora_getitem__(cls, arg, /):"
            f"    return cls.classchora.__getitem__(arg, {defkws})"
            )))
        cls._chora_getitem__ = eval('_chora_getitem__')

        for name in chcls.chorameths:
            new = f"class_{name}"
            exec('\n'.join((
                f"@classmethod",
                f"@_functools.wraps(chcls.{name})",
                f"def {new}(cls, /, *args):",
                f"    return cls.classchora.{name}(*args, {defkws})",
                )))
            setattr(cls, new, eval(new))

    ### Initialising the class:

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.classchora = cls._get_classchora()
        cls._class_defer_chora_methods()


class BythosBase(metaclass=Bythos):

    ClassChora = _chora.Sliceable

    @classmethod
    def _get_classchora(cls, /) -> 'Chora':
        return cls.ClassChora()

    @classmethod
    def _ptolemaic_getitem__(cls, arg, /):
        return cls._chora_getitem__(arg)

    @classmethod
    def _ptolemaic_contains__(cls, arg, /):
        return arg in cls.clschora

    @classmethod
    def __init_subclass__(cls, /, **kwargs):
        with cls.clsmutable:
            super().__init_subclass__(**kwargs)


###############################################################################
###############################################################################
