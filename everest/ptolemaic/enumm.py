###############################################################################
''''''
###############################################################################


import abc as _abc

from .ousia import Ousia as _Ousia


class Enumm(_Ousia):

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.add_enumerators()

    def __iter__(self, /):
        return iter(self.enumerators)


class EnummBase(metaclass=_Ousia):

    __req_slots__ = ('serial', 'name', 'value')
    MERGENAMES = (('__enumerators__', dict),)
    __enumerators__ = {}

    @classmethod
    def add_enumerators(cls, /):
        enumerators = []
        for serial, (name, value) in enumerate(cls.__enumerators__.items()):
            obj = cls(serial=serial, name=name, value=value)
            setattr(cls, name, obj)
            enumerators.append(obj)
        cls.enumerators = tuple(enumerators)

    def __repr__(self, /):
        return f"{self.rootrepr}.{self.name}"

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        return ptolcls.taphonomy.getattr_epitaph(ptolcls, self.name)

    def __class_getitem__(cls, arg: int, /):
        return cls.enumerators[arg]

    @classmethod
    def _yield_concrete_slots(cls, /):
        yield from super()._yield_concrete_slots()
        yield from cls.__enumerators__


###############################################################################
###############################################################################
