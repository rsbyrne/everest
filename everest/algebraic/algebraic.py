###############################################################################
''''''
###############################################################################


from everest.ptolemaic.essence import Essence as _Essence


ALGEBRAICMETHODS = (
    '__armature_brace__', '__armature_truss__',
    '__armature_variable__', '__armature_generic__'
    )


class Algebraic(metaclass=_Essence):

    for methname in ALGEBRAICMETHODS:
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    raise NotImplementedError",
            )))
    del methname


###############################################################################
###############################################################################


        # @classmethod
        # def __class_init__(cls, /):
        #     super().__class_init__()
        #     cls.register(cls.Degenerate)
