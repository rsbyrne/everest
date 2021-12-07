###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.utilities import switch as _switch


class ClassInit:

    __slots__ = ()

    @classmethod
    def __init_subclass__(cls, /, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__class_init__()

    @classmethod
    def __class_init__(cls, /):
        pass


class Freezable(_abc.ABC):

    __slots__ = ()

    @property
    def freezeattr(self, /):
        try:
            return self._freezeattr
        except AttributeError:
            super().__setattr__(
                '_freezeattr', switch := _switch.Switch(False)
                )
            return switch

    @freezeattr.setter
    def freezeattr(self, val, /):
        self._freezeattr.toggle(val)

    @property
    def mutable(self, /):
        return self.freezeattr.as_(False)

    def __setattr__(self, key, val, /):
        if self.freezeattr:
            raise AttributeError(
                f"Setting attributes on an object of type {type(self)} "
                "is forbidden at this time; "
                f"toggle switch `.freezeattr` to override."
                )
        super().__setattr__(key, val)


class FreezableMeta(_abc.ABCMeta):

    @property
    def clsfreezeattr(cls, /):
        try:
            return cls.__dict__['_clsfreezeattr']
        except KeyError:
            super().__setattr__(
                '_clsfreezeattr', switch := _switch.Switch(False)
                )
            return switch

    @clsfreezeattr.setter
    def clsfreezeattr(cls, val, /):
        cls._clsfreezeattr.toggle(val)

    @property
    def clsmutable(cls, /):
        return cls.clsfreezeattr.as_(False)

    def __setattr__(cls, key, val, /):
        if cls.clsfreezeattr:
            raise AttributeError(
                f"Setting attributes on an object of type {type(cls)} "
                "is forbidden at this time; "
                f"toggle switch `.freezeattr` to override."
                )
        super().__setattr__(key, val)


###############################################################################
###############################################################################
