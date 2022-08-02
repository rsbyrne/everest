###############################################################################
''''''
###############################################################################


from everest.ptolemaic.essence import Essence as _Essence


ALGEBRAICMETHODS = (
    '__chdclass_brace__', '__chdclass_truss__',
    '__chdclass_variable__', '__chdclass_generic__'
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
