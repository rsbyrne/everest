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

    @classmethod
    def body_handle_anno(meta, body, name, hint, val, /):
        body['__enumerators__'][name] = (hint, val)
        body['__req_slots__'].append(name)

    def __iter__(cls, /):
        return iter(cls.enumerators)


class _EnummBase_(metaclass=Enumm):

    __enumerators__ = {}
    __fields__ = ('serial', 'name', 'hint', 'value')
    __slots__ = ('_params', *__fields__)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.add_enumerators()

    @classmethod
    def add_enumerators(cls, /):
        enumerators = []
        for serial, (name, args) in enumerate(cls.__enumerators__.items()):
            obj = cls.semi_call(serial, name, *args)
            setattr(cls, name, obj)
            enumerators.append(obj)
        cls.enumerators = enumerators

    @property
    def params(self, /):
        return self._params

    @params.setter
    def params(self, value, /):
        self._params = value
        for key, val in zip(self.__fields__, value):
            setattr(self, key, val)

    def _content_repr(self, /):
        return ', '.join(map(repr, self.params))

    def __repr__(self, /):
        return f"{self.rootrepr}.{self.name}"

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        return ptolcls.taphonomy.getattr_epitaph(ptolcls, self.name)

    def __class_getitem__(cls, arg: int, /):
        return cls.enumerators[arg]


###############################################################################
###############################################################################
