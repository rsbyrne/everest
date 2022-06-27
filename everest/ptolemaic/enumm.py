###############################################################################
''''''
###############################################################################


import abc as _abc

from everest import ur as _ur

from . import ptolemaic as _ptolemaic
from .ousia import Ousia as _Ousia


class Enumm(_Ousia):

    @classmethod
    def _yield_mergenames(meta, body, /):
        yield from super()._yield_mergenames(body)
        yield ('__enumerators__', dict, _ur.DatDict)

    @classmethod
    def body_handle_anno(meta, body, name, hint, val, /):
        body['__enumerators__'][name] = (hint, val)
        body['__req_slots__'][name] = hint

    def __iter__(cls, /):
        return iter(cls.enumerators)

    @property
    def __call__(cls, /):
        raise TypeError("Cannot manually call an Enumm type.")

    @property
    def __class_call__(cls, /):
        raise TypeError("Cannot manually call an Enumm type.")

    @property
    def construct(cls, /):
        raise TypeError("Cannot manually call an Enumm type.")

    @property
    def retrieve(cls, /):
        raise TypeError("Cannot manually call an Enumm type.")

    @property
    def instantiate(cls, /):
        raise TypeError("Cannot manually call an Enumm type.")


class _EnummBase_(metaclass=Enumm):

    __enumerators__ = {}
    __fields__ = ('serial', 'name', 'value')
    __slots__ = ('params', *__fields__)

    @classmethod
    def _get_signature(cls, /):
        return None

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.add_enumerators()

    @classmethod
    def add_enumerators(cls, /):
        enumerators = []
        _it = enumerate(cls.__enumerators__.items())
        for serial, (name, (hint, val)) in _it:
            obj = cls._instantiate_(_ptolemaic.convert((serial, name, val)))
            setattr(cls, name, obj)
            obj.__set_name__(cls, name)
            enumerators.append(obj)
        cls.enumerators = enumerators

    def __getattr__(self, name, /):
        try:
            val = dict(zip(self.__fields__, self.params))[name]
        except KeyError as exc:
            raise AttributeError from exc
        object.__setattr__(self, name, val)
        return val

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
