###############################################################################
''''''
###############################################################################


import abc as _abc

from everest import ur as _ur

from .ousia import Ousia as _Ousia


class Enumm(_Ousia):

    @classmethod
    def _yield_mergenames(meta, /):
        yield from super()._yield_mergenames()
        yield ('__enumerators__', dict, _ur.DatDict)

    def __iter__(cls, /):
        return iter(cls.enumerators)


class _EnummBase_(metaclass=Enumm):

    __enumerators__ = {}
    __slots__ = ('_params', 'serial', 'name', 'value')

    @classmethod
    def classbody_finalise(meta, body, /):
        super().classbody_finalise(body)
        body['__req_slots__'].extend(body['__enumerators__'])

    @classmethod
    def __class_deep_init__(cls, /):
        super().__class_deep_init__()
        cls.add_enumerators()

    @classmethod
    def add_enumerators(cls, /):
        enumerators = []
        for serial, (name, value) in enumerate(cls.__enumerators__.items()):
            obj = cls(serial=serial, name=name, value=value)
            setattr(cls, name, obj)
            enumerators.append(obj)
        cls.enumerators = tuple(enumerators)

    @property
    def params(self, /):
        return self._params

    @params.setter
    def params(self, value, /):
        self._params = value
        for key, val in zip(('serial', 'name', 'value'), params):
            setattr(self, key, val)

    def __repr__(self, /):
        return f"{self.rootrepr}.{self.name}"

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        return ptolcls.taphonomy.getattr_epitaph(ptolcls, self.name)

    def __class_getitem__(cls, arg: int, /):
        return cls.enumerators[arg]


###############################################################################
###############################################################################
